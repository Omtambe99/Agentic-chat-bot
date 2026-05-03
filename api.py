#!/usr/bin/env python3
"""
Vera Challenge — Judge-compatible HTTP server.

This server exposes the challenge contract under /v1/* and keeps the legacy
compose endpoint for local compatibility with the existing helper scripts.

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8080
"""

import copy
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
import uvicorn
import asyncio

from bot import compose, compose_async


class ComposeRequest(BaseModel):
    category: Dict[str, Any] = Field(..., description="CategoryContext dict")
    merchant: Dict[str, Any] = Field(..., description="MerchantContext dict")
    trigger: Dict[str, Any] = Field(..., description="TriggerContext dict")
    customer: Optional[Dict[str, Any]] = Field(None, description="CustomerContext dict (optional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": {
                    "slug": "dentists",
                    "voice": {"tone": "peer_clinical"},
                    "offer_catalog": [{"id": "den_001", "title": "Dental Cleaning @ ₹299"}],
                },
                "merchant": {
                    "merchant_id": "m_001_drmeera_dentist_delhi",
                    "category_slug": "dentists",
                    "identity": {"name": "Dr. Meera's Dental Clinic", "city": "Delhi"},
                    "performance": {"views": 2410, "calls": 18, "ctr": 0.021},
                    "offers": [{"title": "Dental Cleaning @ ₹299", "status": "active"}],
                    "conversation_history": [],
                },
                "trigger": {
                    "id": "trg_001_research_digest_dentists",
                    "kind": "research_digest",
                    "scope": "merchant",
                    "payload": {"top_item": {"title": "New research on fluoride"}},
                },
                "customer": None,
            }
        }
    )


class ComposeResponse(BaseModel):
    body: str = Field(..., description="The WhatsApp message body")
    cta: str = Field(..., description="Call-to-action type: YES/STOP, open_ended, or none")
    send_as: str = Field(..., description="Recipient: vera or merchant_on_behalf")
    suppression_key: str = Field(..., description="Deduplication key")
    rationale: str = Field(..., description="Why this message was composed")


class HealthResponse(BaseModel):
    status: str = "healthy"
    message: str = "Vera API is running"


class ContextPushRequest(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str


class TickRequest(BaseModel):
    now: str
    available_triggers: list[str] = Field(default_factory=list)


class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: Literal["merchant", "customer"]
    message: str
    received_at: str
    turn_number: int


class TickAction(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: str
    trigger_id: str
    template_name: str
    template_params: list[str] = Field(default_factory=list)
    body: str
    cta: str
    suppression_key: str
    rationale: str


class TickResponse(BaseModel):
    actions: list[TickAction] = Field(default_factory=list)


class ReplyResponse(BaseModel):
    action: Literal["send", "wait", "end"]
    body: Optional[str] = None
    cta: Optional[str] = None
    wait_seconds: Optional[int] = None
    rationale: str


class ContextAck(BaseModel):
    accepted: bool
    ack_id: Optional[str] = None
    stored_at: Optional[str] = None
    reason: Optional[str] = None
    current_version: Optional[int] = None


TEAM_NAME = "Team Alpha"
TEAM_MEMBERS = ["Alice", "Bob"]
MODEL_NAME = "deterministic-composer-v1"
APPROACH = "single-prompt composer with retrieval over pushed context and trigger dispatch"
CONTACT_EMAIL = "team@example.com"
VERSION = "1.2.0"
SUBMITTED_AT = "2026-04-26T08:00:00Z"

START_TIME = time.time()
CONTEXTS: dict[tuple[str, str], dict[str, Any]] = {}
CONVERSATIONS: dict[str, dict[str, Any]] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _context_counts() -> Dict[str, int]:
    counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
    for (scope, _), _record in CONTEXTS.items():
        if scope in counts:
            counts[scope] += 1
    return counts


def _get_context(scope: str, context_id: str) -> Optional[Dict[str, Any]]:
    record = CONTEXTS.get((scope, context_id))
    if not record:
        return None
    return record["payload"]


def _merchant_context_for_conversation(merchant: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
    merchant_copy = copy.deepcopy(merchant)
    history = CONVERSATIONS.get(conversation_id, {}).get("history", [])
    if history:
        merchant_copy["conversation_history"] = history
    return merchant_copy


def _record_turn(conversation_id: str, role: str, body: str, meta: Optional[Dict[str, Any]] = None) -> None:
    state = CONVERSATIONS.setdefault(conversation_id, {"history": [], "meta": {}})
    state["history"].append({
        "from": role,
        "body": body,
        "timestamp": _utc_now_iso(),
        **(meta or {}),
    })


def _reply_keywords(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ("stop", "not interested", "no thanks", "unsubscribe", "leave me")):
        return "end"
    if any(word in lowered for word in ("later", "busy", "tomorrow", "call later", "not now", "after", "someday")):
        return "wait"
    if any(word in lowered for word in ("yes", "send", "ok", "okay", "let's do it", "lets do it", "go ahead", "sure")):
        return "send"
    return "send"


def _template_name(trigger_kind: str) -> str:
    normalized = trigger_kind or "generic"
    normalized = normalized.replace("/", "_").replace(" ", "_")
    return f"vera_{normalized}_v1"


async def _compose_action(category: Dict[str, Any], merchant: Dict[str, Any], trigger: Dict[str, Any], customer: Optional[Dict[str, Any]], conversation_id: str) -> TickAction:
    result = await compose_async(category=category, merchant=merchant, trigger=trigger, customer=customer)
    merchant_id = merchant.get("merchant_id") or merchant.get("identity", {}).get("merchant_id") or conversation_id
    customer_id = (customer or {}).get("customer_id")
    trigger_id = trigger.get("id") or trigger.get("context_id") or trigger.get("suppression_key") or conversation_id
    template_name = _template_name(trigger.get("kind", "generic"))
    template_params = [
        merchant.get("identity", {}).get("name") or merchant_id,
        trigger.get("kind", "generic"),
    ]
    return TickAction(
        conversation_id=conversation_id,
        merchant_id=merchant_id,
        customer_id=customer_id,
        send_as=result["send_as"],
        trigger_id=trigger_id,
        template_name=template_name,
        template_params=template_params,
        body=result["body"],
        cta=result["cta"],
        suppression_key=result["suppression_key"],
        rationale=result["rationale"],
    )


def _reply_from_trigger(trigger: Dict[str, Any], merchant: Dict[str, Any], customer: Optional[Dict[str, Any]], message: str) -> ReplyResponse:
    trigger_kind = (trigger or {}).get("kind", "")
    merchant_name = merchant.get("identity", {}).get("name") or merchant.get("merchant_id", "merchant")
    customer_name = (customer or {}).get("identity", {}).get("name")
    next_step = _reply_keywords(message)

    if next_step == "end":
        return ReplyResponse(
            action="end",
            rationale="The reply clearly indicates no interest or opt-out, so the conversation should end cleanly.",
        )

    if next_step == "wait":
        return ReplyResponse(
            action="wait",
            wait_seconds=1800,
            rationale="The reply indicates the user is busy or wants time, so the bot should back off for 30 minutes.",
        )

    if trigger_kind in {"recall_due", "appointment_tomorrow", "trial_followup"} or customer_name:
        body = f"Hi {customer_name or 'there'}, understood — I’ll keep this short and action-ready from {merchant_name}. Reply YES to continue or STOP to pause."
        return ReplyResponse(
            action="send",
            body=body,
            cta="YES/STOP",
            rationale="Customer-facing follow-up should stay low-friction and consent-aware.",
        )

    if trigger_kind in {"research_digest", "regulation_change", "perf_spike", "perf_dip", "renewal_due", "subscription_expiry", "active_planning_intent", "merchant_join_intent", "dormant_with_vera", "stale_posts", "festival_upcoming", "seasonal_promo", "review_theme_emerged", "competitor_opened"}:
        body = f"{merchant_name}, got it — I can turn this into the next concrete step now. Want the short version, or should I draft the message for you?"
        return ReplyResponse(
            action="send",
            body=body,
            cta="open_ended",
            rationale="The merchant is engaged, so the next move is to advance with one specific low-effort option.",
        )

    body = f"{merchant_name}, understood — I’ll keep this focused on the current signal. Want me to continue?"
    return ReplyResponse(
        action="send",
        body=body,
        cta="open_ended",
        rationale="Default response keeps the conversation on-mission while inviting one clear next step.",
    )


app = FastAPI(
    title="Vera Merchant AI Assistant",
    description="Judge-compatible message engine for merchant engagement.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.get("/v1/healthz")
async def healthz():
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - START_TIME),
        "contexts_loaded": _context_counts(),
    }


@app.get("/v1/metadata")
async def metadata():
    return {
        "team_name": TEAM_NAME,
        "team_members": TEAM_MEMBERS,
        "model": MODEL_NAME,
        "approach": APPROACH,
        "contact_email": CONTACT_EMAIL,
        "version": VERSION,
        "submitted_at": SUBMITTED_AT,
    }


@app.post("/v1/context", response_model=ContextAck, response_model_exclude_none=True)
async def push_context(request: ContextPushRequest):
    if request.scope not in {"category", "merchant", "customer", "trigger"}:
        return JSONResponse(
            status_code=400,
            content={"accepted": False, "reason": "invalid_scope", "details": f"Unsupported scope: {request.scope}"},
        )

    key = (request.scope, request.context_id)
    current = CONTEXTS.get(key)
    if current and current["version"] >= request.version:
        return JSONResponse(
            status_code=409,
            content={
                "accepted": False,
                "reason": "stale_version",
                "current_version": current["version"],
            },
        )

    CONTEXTS[key] = {
        "version": request.version,
        "payload": copy.deepcopy(request.payload),
        "delivered_at": request.delivered_at,
        "stored_at": _utc_now_iso(),
    }
    return ContextAck(
        accepted=True,
        ack_id=f"ack_{request.context_id}_v{request.version}",
        stored_at=CONTEXTS[key]["stored_at"],
    )


@app.post("/v1/tick", response_model=TickResponse)
async def tick(request: TickRequest):
    tasks = []
    for trigger_id in request.available_triggers[:20]:
        trigger = _get_context("trigger", trigger_id)
        if not trigger:
            continue

        merchant_id = trigger.get("merchant_id")
        merchant = _get_context("merchant", merchant_id) if merchant_id else None
        if not merchant:
            continue

        category_slug = merchant.get("category_slug") or trigger.get("payload", {}).get("category")
        category = _get_context("category", category_slug) if category_slug else None
        if not category:
            continue

        customer_id = trigger.get("customer_id")
        customer = _get_context("customer", customer_id) if customer_id else None

        conversation_id = f"conv_{merchant_id}_{trigger_id}_{uuid.uuid4().hex[:8]}"
        merchant_for_compose = _merchant_context_for_conversation(merchant, conversation_id)
        
        tasks.append((
            conversation_id, merchant_id, customer_id, trigger_id,
            _compose_action(category, merchant_for_compose, trigger, customer, conversation_id)
        ))

    actions: list[TickAction] = []
    if tasks:
        coros = [t[4] for t in tasks]
        results = await asyncio.gather(*coros)
        for i, action in enumerate(results):
            actions.append(action)
            conv_id, m_id, c_id, t_id, _ = tasks[i]
            state = CONVERSATIONS.setdefault(conv_id, {"history": [], "meta": {}})
            state["meta"].update({"merchant_id": m_id, "customer_id": c_id, "trigger_id": t_id})
            _record_turn(conv_id, "vera", action.body, {
                "trigger_id": t_id,
                "send_as": action.send_as,
            })

    return TickResponse(actions=actions)


@app.post("/v1/reply", response_model=ReplyResponse, response_model_exclude_none=True)
async def reply(request: ReplyRequest):
    state = CONVERSATIONS.setdefault(request.conversation_id, {"history": [], "meta": {}})
    state["meta"].update({
        "merchant_id": request.merchant_id,
        "customer_id": request.customer_id,
        "last_turn_number": request.turn_number,
        "received_at": request.received_at,
    })
    _record_turn(request.conversation_id, request.from_role, request.message, {
        "turn_number": request.turn_number,
    })

    trigger_id = state["meta"].get("trigger_id")
    merchant_id = request.merchant_id or state["meta"].get("merchant_id")
    customer_id = request.customer_id or state["meta"].get("customer_id")
    merchant = _get_context("merchant", merchant_id) if merchant_id else None
    customer = _get_context("customer", customer_id) if customer_id else None
    trigger = _get_context("trigger", trigger_id) if trigger_id else None

    if merchant and trigger:
        response = _reply_from_trigger(trigger, merchant, customer, request.message)
    else:
        lowered = request.message.lower()
        if any(word in lowered for word in ("stop", "not interested", "unsubscribe")):
            response = ReplyResponse(action="end", rationale="Reply indicates opt-out.")
        elif any(word in lowered for word in ("later", "busy", "tomorrow")):
            response = ReplyResponse(action="wait", wait_seconds=1800, rationale="Reply indicates delay.")
        else:
            response = ReplyResponse(
                action="send",
                body="Understood — I’ll keep this concise and send the next useful step.",
                cta="open_ended",
                rationale="Fallback reply handling keeps the conversation moving without guessing context.",
            )

    if response.action == "send" and response.body:
        _record_turn(request.conversation_id, "vera", response.body, {"reply_action": "send"})

    return response


@app.post("/v1/teardown")
async def teardown():
    CONTEXTS.clear()
    CONVERSATIONS.clear()
    return {"ok": True}


@app.post("/compose", response_model=ComposeResponse)
async def compose_message(request: ComposeRequest):
    """
    Compose a WhatsApp message given category, merchant, trigger, and optional customer contexts.

    Returns a dict with body, cta, send_as, suppression_key, and rationale.
    """
    try:
        result = await compose_async(
            category=request.category,
            merchant=request.merchant,
            trigger=request.trigger,
            customer=request.customer,
        )
        return ComposeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Composition failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API documentation link."""
    return {
        "message": "Vera AI Challenge API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# =============================================================================
# Development runner
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
