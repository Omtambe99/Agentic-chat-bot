import json
import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any, Iterable
from dotenv import load_dotenv

# Load environment variables from a .env file (if one exists)
load_dotenv()

AUTO_REPLY_MARKERS = (
    "thank you for contacting",
    "thanks for contacting",
    "we will get back to you",
    "i am currently unavailable",
    "main ek automated assistant hoon",
    "this is an automated response",
)

def _latest_message(history: Iterable[Dict[str, Any]], sender: str) -> str:
    for item in reversed(list(history or [])):
        if item.get("from") == sender:
            return item.get("body", "") or ""
    return ""

def _salutation(category: Dict[str, Any], merchant: Dict[str, Any]) -> str:
    voice = category.get("voice", {})
    first_name = merchant.get("identity", {}).get("owner_first_name")
    examples = voice.get("salutation_examples") or []
    if first_name and examples:
        template = examples[0]
        safe_values = {
            "first_name": first_name,
            "owner_first_name": first_name,
            "chef_or_owner_first_name": first_name,
            "merchant_name": merchant.get("identity", {}).get("name", "there"),
        }
        try:
            return template.format(**safe_values)
        except KeyError:
            for key, value in safe_values.items():
                template = template.replace("{" + key + "}", value)
            return template
    if first_name:
        return f"Hi {first_name}"
    return f"Hi {merchant.get('identity', {}).get('name', 'there')}"

def _merchant_name(merchant: Dict[str, Any]) -> str:
    return merchant.get("identity", {}).get("name") or merchant.get("merchant_id", "merchant")

def _best_offer_title(category: Dict[str, Any], merchant: Dict[str, Any]) -> Optional[str]:
    active_offers = [offer for offer in merchant.get("offers", []) if offer.get("status") == "active"]
    if active_offers:
        return active_offers[0].get("title")
    catalog = category.get("offer_catalog") or []
    if catalog:
        first = catalog[0]
        if isinstance(first, dict):
            return first.get("title")
        return str(first)
    return None

def compose_deterministic(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Dict[str, Any], customer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Deterministic fallback in case LLM fails."""
    merchant_name = _merchant_name(merchant)
    salutation = _salutation(category, merchant)

    trigger_kind = trigger.get("kind", "")
    suppression_key = trigger.get("suppression_key") or trigger.get("id")
    history = merchant.get("conversation_history") or []
    last_merchant_message = _latest_message(history, "merchant")
    latest_human_text = last_merchant_message or _latest_message(history, "vera")
    auto_reply_detected = any(marker in latest_human_text.lower() for marker in AUTO_REPLY_MARKERS)

    if auto_reply_detected:
        body = f"{salutation}, samajh gaya — yeh auto-reply lag raha hai. Main owner/manager ko directly route karta hoon."
        cta = "none"
        send_as = "vera"
        rationale = "Auto-reply detected, route to right person."

    elif trigger_kind.startswith("research_digest"):
        top = trigger.get("payload", {}).get("top_item", {})
        title = top.get("title") or top.get("headline") or "a new research update"
        source = top.get("source") or trigger.get("payload", {}).get("source")
        body = f"{salutation}, heads-up: trending content — {title}"
        if source: body += f" ({source})"
        body += ". 1-line summary & ready post draft?"
        cta = "open_ended"
        send_as = "vera"
        rationale = "Research digest with heads-up + specificity from title."

    elif trigger_kind in ("perf_spike", "perf_dip", "perf_change", "seasonal_perf_dip"):
        metric = trigger.get("payload", {}).get("metric") or "performance"
        delta = trigger.get("payload", {}).get("delta_pct")
        if delta is not None:
            direction = "up" if delta >= 0 else "down"
            delta_pct = f"{abs(round(delta * 100))}%"
            body = f"{salutation}, heads-up: {metric} is {direction} {delta_pct} vs baseline. Want me to draft the next offer/post?"
        else:
            body = f"{salutation}, noticed a performance update on your dashboard. Want a short checklist to improve discovery?"
        cta = "YES/STOP"
        send_as = "vera"
        rationale = "Performance change with specificity."

    elif trigger_kind in ("renewal_due", "subscription_expiry"):
        amount = trigger.get("payload", {}).get("renewal_amount")
        body = f"{salutation}, renewal is due"
        if amount is not None: body += f" (₹{amount})"
        body += ". Want the 1-line renewal summary?"
        cta = "open_ended"
        send_as = "vera"
        rationale = "Renewal trigger with amount."

    elif trigger_kind.startswith("customer_") or trigger.get("scope") == "customer" or customer is not None:
        cust_name = (customer or {}).get("identity", {}).get("name", "there")
        send_as = "merchant_on_behalf"
        body = f"Hi {cust_name}, {merchant_name} has a quick follow-up for you. Reply YES if you want the next available slot."
        cta = "YES/STOP"
        rationale = "Customer-facing reminder."

    else:
        body = f"{salutation}, heads-up: something interesting might help you grow. Want to discuss?"
        cta = "open_ended"
        send_as = "vera"
        rationale = "Generic heads-up for unclassified triggers."

    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": str(suppression_key),
        "rationale": rationale,
    }

async def compose_async(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Dict[str, Any], customer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Falling back to deterministic bot.")
        return compose_deterministic(category, merchant, trigger, customer)

    history = merchant.get("conversation_history") or []
    last_merchant_message = _latest_message(history, "merchant")
    latest_human_text = last_merchant_message or _latest_message(history, "vera")
    auto_reply_detected = any(marker in latest_human_text.lower() for marker in AUTO_REPLY_MARKERS)

    if auto_reply_detected:
        return compose_deterministic(category, merchant, trigger, customer)

    # Prepare context for LLM
    context = {
        "category": {
            "slug": category.get("slug"),
            "voice": category.get("voice"),
            "taboos": category.get("voice", {}).get("vocab_taboo", [])
        },
        "merchant": {
            "name": merchant.get("identity", {}).get("name"),
            "owner": merchant.get("identity", {}).get("owner_first_name"),
            "locality": merchant.get("identity", {}).get("locality"),
            "languages": merchant.get("identity", {}).get("languages"),
            "performance": merchant.get("performance"),
            "offers": [o.get("title") for o in merchant.get("offers", []) if o.get("status") == "active"],
            "last_message": last_merchant_message
        },
        "trigger": {
            "kind": trigger.get("kind"),
            "scope": trigger.get("scope"),
            "payload": trigger.get("payload"),
            "urgency": trigger.get("urgency")
        },
        "customer": customer.get("identity") if customer else None
    }

    system_prompt = """You are Vera, magicpin's AI assistant for merchant growth.
You must output ONLY valid JSON format representing the next message to send.

JSON Format Requirements:
{
  "body": "<the message text to send>",
  "cta": "<YES/STOP, open_ended, or none>",
  "send_as": "<vera or merchant_on_behalf>",
  "suppression_key": "<unique string for deduplication>",
  "rationale": "<brief reason why this message fits>"
}

Writing Guidelines:
1. SPECIFICITY: Include exact numbers (e.g., ₹299, 15%), dates, local areas (from the locality field), and specific offer names.
2. CATEGORY FIT: Adopt the exact voice specified in the category context (e.g., clinical for dentists, warm for salons).
3. MERCHANT FIT: Personalize to the merchant owner's name. If 'languages' includes 'hi' (Hindi), seamlessly sprinkle a few natural Hindi words (Hinglish) into the message for authenticity.
4. TRIGGER RELEVANCE: Always address the exact "Why Now?" from the trigger kind and payload. Connect the data to a specific action.
5. ENGAGEMENT: Have one clear CTA. Prefer "YES/STOP" if proposing an action. Do not use generic filler copy. Never make up fake numbers or claims; strictly rely on the provided context payload and performance data. Keep asks short.
"""

    user_prompt = f"Context: {json.dumps(context, indent=2)}\n\nGenerate the JSON output for the next message."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": system_prompt + "\n\n" + user_prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    res = json.loads(text)
                    return {
                        "body": res.get("body", "Hello"),
                        "cta": res.get("cta", "YES/STOP"),
                        "send_as": res.get("send_as", "vera"),
                        "suppression_key": str(res.get("suppression_key", trigger.get("id"))),
                        "rationale": res.get("rationale", "LLM Generated"),
                    }
                else:
                    print(f"LLM API Error: {response.status} - {await response.text()}")
    except Exception as e:
        print(f"LLM request failed: {e}")

    # Fallback if anything goes wrong
    return compose_deterministic(category, merchant, trigger, customer)

def compose(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Dict[str, Any], customer: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Synchronous wrapper for legacy compatibility."""
    try:
        loop = asyncio.get_running_loop()
        raise RuntimeError("compose() called synchronously from a running event loop! Use compose_async instead.")
    except RuntimeError:
        return asyncio.run(compose_async(category, merchant, trigger, customer))
