# Vera Challenge — Quick Visual Code Flow Reference

## High-Level Flow (1 minute read)

```
JUDGE
  ↓ Sends merchant/trigger data
VERA API (api.py)
  ↓ Validates request
BOT COMPOSER (bot.py)
  ↓ Generates message
API RESPONSE
  ↓ Returns JSON
JUDGE SCORES
```

---

## Phase-by-Phase Quick Reference

### PHASE 1: Judge Initiates Request

**What:** Judge sends HTTP POST with merchant/trigger/category

```json
POST /compose
{
  "category": {"slug": "dentists", "voice": {...}},
  "merchant": {"merchant_id": "m_001", "identity": {...}, "performance": {...}},
  "trigger": {"kind": "renewal_due", "payload": {...}},
  "customer": null
}
```

---

### PHASE 2: API Validation (api.py, 20ms)

**What:** FastAPI receives request, Pydantic validates structure

```python
@app.post("/compose")
async def compose_endpoint(request: ComposeRequest):
    # Pydantic validates: required fields, data types
    # Extract: category, merchant, trigger, customer
    # Call bot.compose()
```

**Validation Checklist:**

- ✅ Required fields present (category, merchant, trigger)
- ✅ Data types correct
- ✅ customer optional (OK to null)

---

### PHASE 3: Bot Composition (bot.py, 80ms)

**What:** Deterministic message generation from 4-context inputs

#### Step 3.1: Context Extraction (5 lines)

```python
merchant_name = merchant.get("identity", {}).get("name")  # "Dr. Meera's Dental Clinic"
salutation = _salutation(category, merchant)              # "Hi Meera"
trigger_kind = trigger.get("kind", "")                    # "renewal_due"
history = merchant.get("conversation_history") or []      # Conversation history
auto_reply_detected = check_for_auto_reply(history)       # True/False
```

#### Step 3.2: Decision Tree (Main Logic)

```
Is auto_reply detected?
├─ YES → Route to human, STOP
└─ NO → Check trigger_kind
    ├─ research_digest → Extract title, compose research message
    ├─ regulation_change → Extract deadline, compose compliance message
    ├─ perf_spike/dip → Extract delta%, compose performance alert
    ├─ renewal_due → Extract days/amount, compose renewal message
    ├─ active_planning_intent → Compose action-ready message
    ├─ customer_* → Extract customer name, compose customer message
    ├─ stale_posts → Extract peer stats, compose refresh message
    ├─ festival_upcoming → Extract festival/offer, compose seasonal message
    ├─ review_theme_emerged → Extract theme/quote, compose response message
    ├─ competitor_opened → Extract distance/offer, compose threat message
    └─ else → Use fallback message
```

#### Step 3.3: Message Composition Pattern (Renewal Trigger Example)

```python
# Extract payload
days_remaining = trigger.get("payload", {}).get("days_remaining")  # 3
plan = trigger.get("payload", {}).get("plan")                      # "Pro plan"
amount = trigger.get("payload", {}).get("renewal_amount")          # 2999

# Build message
body = f"{salutation}, renewal is due"                # "Hi Meera, renewal is due"
if days_remaining:
    body += f" in {days_remaining} days"              # "Hi Meera, renewal is due in 3 days"
if plan:
    body += f" for {plan}"                            # "Hi Meera, renewal is due in 3 days for Pro plan"
if amount:
    body += f" (₹{amount})"                           # "Hi Meera, renewal is due in 3 days for Pro plan (₹2999)"
body += ". Want the 1-line renewal summary?"

# Set metadata
cta = "open_ended"                                     # How merchant can respond
send_as = "vera"                                       # Who sends (vera or merchant_on_behalf)
suppression_key = "renewal:m_001:2026"                 # Prevent duplicates
rationale = "Renewal with due keyword + amount..."     # Why this message
```

#### Step 3.4: Return Structured Output

```python
return {
    "body": "Hi Meera, renewal is due in 3 days for Pro plan (₹2999). Want the 1-line renewal summary?",
    "cta": "open_ended",
    "send_as": "vera",
    "suppression_key": "renewal:m_001:2026",
    "rationale": "Renewal with due keyword + amount for specificity."
}
```

---

### PHASE 4: Response Validation & Return (api.py, <1ms)

**What:** Pydantic validates output, serialize to JSON

```python
# Validate output
response = ComposeResponse(
    body=result["body"],
    cta=result["cta"],
    send_as=result["send_as"],
    suppression_key=result["suppression_key"],
    rationale=result["rationale"]
)

# Return HTTP 200 OK + JSON
{
  "body": "Hi Meera, renewal is due in 3 days for Pro plan (₹2999). Want the 1-line renewal summary?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "renewal:m_001:2026",
  "rationale": "Renewal with due keyword + amount for specificity."
}
```

---

### PHASE 5: Judge Scores Response

**What:** Judge evaluates on 5 dimensions (0-10 each = 50 max)

#### Scoring Breakdown (for renewal message example):

**SPECIFICITY (7/10):**

```
✓ Contains number "3" → +4
✓ Contains rupee "₹2999" → +2
✗ No date (e.g., 2026-05-03)
✓ Length > 80 chars → +1
────────────────
Total: 7/10
```

**CATEGORY FIT (5/10):**

```
Base: 5
✗ No category word (dental, salon, etc.)
✗ No category-specific keyword (fluoride, post, etc.)
────────────────
Total: 5/10
```

**MERCHANT FIT (5/10):**

```
✓ "Hi Meera" contains "Hi" → +2
✓ "renewal" is merchant context → +3
────────────────
Total: 5/10
```

**TRIGGER RELEVANCE (6/10):**

```
✓ "due" keyword → +4
✓ "open_ended" CTA type → +2
────────────────
Total: 6/10
```

**ENGAGEMENT (6/10):**

```
✗ CTA is "open_ended" (not YES/STOP)
✓ "Want" + "summary" keywords → +4
✓ "1-line" urgency word → +2
────────────────
Total: 6/10
```

**FINAL SCORE: 7 + 5 + 5 + 6 + 6 = 29/50**

---

### PHASE 6: Submission Generation (submission_generator.py)

**What:** Builds 30-line JSONL from expanded dataset

```
Load 100 triggers from dataset
    ↓
Sample 30 random triggers
    ↓
For each trigger:
  - Get merchant from trigger.merchant_id
  - Get category from merchant.category_slug
  - Call compose(category, merchant, trigger)
  - Add test_id, body, cta, send_as, suppression_key, rationale
  - Write to JSONL line
    ↓
Output: submission.jsonl (30 lines)
```

**Each line format:**

```json
{
  "test_id": "trg_renewal_due_m001",
  "body": "Hi Meera, renewal is due in 3 days for Pro plan (₹2999). Want the 1-line renewal summary?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "renewal:m_001:2026",
  "rationale": "Renewal with due keyword + amount for specificity."
}
```

---

### PHASE 7: Validation (evaluate_submission.py)

**What:** Checks each JSONL line meets constraints

```
Load submission.jsonl
    ↓
For each line:
  ✅ Parse JSON
  ✅ Check required keys present
  ✅ Check CTA in {YES/STOP, open_ended, none}
  ✅ Check send_as in {vera, merchant_on_behalf}
  ✅ Check body length (0-160 chars)
  ✅ Check for duplicates
    ↓
Output: {count: 30, valid: true, problems: []}
```

---

## Key Decision Points in Code

### Decision 1: Auto-reply Detection

```
Latest message in conversation contains:
  - "thank you for contacting"
  - "i am currently unavailable"
  - "this is an automated response"
  etc.
    ↓ YES
    Send routing message, CTA=none, STOP
    ↓ NO
    Continue to trigger classification
```

### Decision 2: Trigger Classification

```
trigger_kind matches one of 15+ patterns?
    ├─ research_digest → Research message
    ├─ regulation_change → Compliance message
    ├─ renewal_due → Renewal reminder
    ├─ perf_spike/dip → Performance alert
    ├─ ... (12 more types)
    └─ else → Fallback message
```

### Decision 3: Customer vs. Merchant

```
trigger.kind.startswith("customer_")
OR trigger.scope == "customer"
OR customer is not None
    ↓ YES
    Send customer-facing message (merchant_on_behalf)
    ↓ NO
    Send merchant-facing message (vera)
```

---

## Data Flow Diagram

```
INPUT DATA
│
├─ category (dict)
│  ├─ slug: "dentists"
│  ├─ voice: {tone, salutation_examples, offer_catalog}
│  └─ peer_stats: {avg_post_freq_days, avg_engagement_rate}
│
├─ merchant (dict)
│  ├─ merchant_id: "m_001"
│  ├─ identity: {name, owner_first_name, category_slug, languages}
│  ├─ performance: {views, impressions, ctr, active_days}
│  ├─ offers: [{id, title, status, discount}]
│  └─ conversation_history: [{from, body, timestamp}]
│
├─ trigger (dict)
│  ├─ id: "trg_001"
│  ├─ kind: "renewal_due"
│  ├─ suppression_key: "renewal:m_001:2026"
│  └─ payload: {days_remaining, plan, renewal_amount, ...}
│
└─ customer (dict, optional)
   ├─ customer_id: "c_001"
   ├─ identity: {name, phone, preferences}
   └─ history: [{booking_date, service, notes}]

           ↓ bot.compose()

OUTPUT MESSAGE
│
├─ body: "Hi Meera, renewal is due in 3 days for Pro plan (₹2999). Want the 1-line renewal summary?"
├─ cta: "open_ended"
├─ send_as: "vera"
├─ suppression_key: "renewal:m_001:2026"
└─ rationale: "Renewal with due keyword + amount for specificity."
```

---

## Trigger Types at a Glance

| Trigger Type           | Extract From                     | Compose Pattern                                          | CTA Type   |
| ---------------------- | -------------------------------- | -------------------------------------------------------- | ---------- |
| research_digest        | top_item.title, source           | "heads-up: trending content — {title}"                   | open_ended |
| regulation_change      | title, deadline_iso              | "heads-up: {title}. Due: {date}"                         | open_ended |
| perf_spike/dip         | metric, delta_pct, vs_baseline   | "{metric} is {direction} {delta}% vs baseline"           | open_ended |
| renewal_due            | days_remaining, plan, amount     | "renewal is due in {days} days for {plan} (₹{amount})"   | open_ended |
| active_planning_intent | intent_topic                     | "perfect — I'll draft {topic} now. Reply YES..."         | YES/STOP   |
| dormant_with_vera      | stale_days, peer_post_freq       | "posts look stale ({stale_days} ago)..."                 | YES/STOP   |
| festival_upcoming      | festival, offer                  | "{festival} is coming — use '{offer}' offer"             | YES/STOP   |
| review_theme_emerged   | theme, common_quote              | "I spotted review theme: {theme}..."                     | open_ended |
| competitor_opened      | competitor_name, distance, offer | "{competitor} opened {distance}km away with {offer}"     | open_ended |
| recall_due             | service, slots, days_overdue     | "It's been {days} since last visit — time for {service}" | YES/STOP   |
| appointment_tomorrow   | days_until, time_slot            | "Your {service} is {day} at {time}. Confirming?"         | YES/STOP   |
| trial_followup         | —                                | "Quick follow-up for you. Reply YES for slot"            | YES/STOP   |
| auto_reply_detected    | —                                | "Auto-reply detected. Routing to owner/manager."         | none       |

---

## Performance Metrics

| Phase       | Component     | Time       | Bottleneck        |
| ----------- | ------------- | ---------- | ----------------- |
| Request     | Network       | 10-50ms    | Network latency   |
| Validation  | Pydantic      | <1ms       | Type checking     |
| Composition | bot.compose() | 5-10ms     | String operations |
| Response    | Serialization | <1ms       | JSON encoding     |
| **Total**   | **API**       | **<100ms** | Network (not us)  |

---

## Error Handling

```
Request arrives
    ↓
Pydantic validation fails?
    ├─ YES → 422 Unprocessable Entity + error details
    └─ NO → Continue

bot.compose() throws exception?
    ├─ YES → 500 Internal Server Error + error message
    └─ NO → Continue

Response validation fails?
    ├─ YES → 500 Internal Server Error
    └─ NO → 200 OK + JSON response
```

---

## Helper Functions Reference

### \_merchant_name(merchant)

```python
Returns: merchant.identity.name or merchant_id
Example: "Dr. Meera's Dental Clinic"
```

### \_salutation(category, merchant)

```python
Returns: Formatted greeting from category voice template
Example: "Hi Meera"
Logic:
  1. Get salutation_examples from category.voice
  2. Format with owner_first_name
  3. If no example, return "Hi {first_name}" or "Hi {name}"
```

### \_latest_message(history, sender)

```python
Returns: Latest message body from specific sender
Searches: conversation_history in reverse order
Sender: "vera" or "merchant"
Example: Returns "" if no messages from sender
```

### \_best_offer_title(category, merchant)

```python
Returns: Best active offer title or category catalog item
Priority:
  1. Active merchant offers
  2. Category offer catalog
  3. None if unavailable
Example: "Whitening discount" or "20% off" or None
```

---

## State & Conversation Management (conversation_handlers.py)

```
Handler tracks per-merchant:
├─ turns: List of message history
├─ engagement_score: YES (+1), STOP (-2)
├─ suppression_keys: Set of "don't re-send" keys
└─ last_message_time: For cooldown calculation

On response from merchant:
├─ "YES" → engagement_score += 1, move to action phase
├─ "STOP" → engagement_score -= 2, suppress further messages
├─ Custom reply → Re-qualify or escalate
└─ Silence → Check cooldown before next trigger
```

---

## Real Example: End-to-End Walkthrough

### Input

```json
{
  "category": {
    "slug": "restaurants",
    "voice": { "salutation_examples": ["Hi {first_name}"] }
  },
  "merchant": {
    "merchant_id": "m_456",
    "identity": { "name": "Taj Masala", "owner_first_name": "Rajesh" }
  },
  "trigger": {
    "kind": "competitor_opened",
    "payload": {
      "competitor_name": "Olive Garden",
      "distance_km": 2,
      "their_offer": "30% off"
    }
  },
  "customer": null
}
```

### Processing

```
1. Extract context:
   - merchant_name = "Taj Masala"
   - salutation = "Hi Rajesh"
   - trigger_kind = "competitor_opened"

2. Match trigger:
   - competitor_opened → Extract distance, offer

3. Compose message:
   body = "Hi Rajesh, Olive Garden just opened nearby (2 km) with 30% off. Want a counter-offer idea that matches your category voice?"
   cta = "open_ended"
   send_as = "vera"
   suppression_key = "competitor:m_456:olive_garden"

4. Score on 5 dimensions:
   - Specificity: 2 (has distance "2 km", company name) → 5/10
   - Category Fit: Restaurant context → 6/10
   - Merchant Fit: Personalized "Hi Rajesh" → 5/10
   - Trigger Relevance: "nearby", "opened", "counter-offer" → 7/10
   - Engagement: "Want", "idea" → 6/10
   - TOTAL: 29/50
```

### Output

```json
{
  "body": "Hi Rajesh, Olive Garden just opened nearby (2 km) with 30% off. Want a counter-offer idea that matches your category voice?",
  "cta": "open_ended",
  "send_as": "vera",
  "suppression_key": "competitor:m_456:olive_garden",
  "rationale": "Competitive trigger: specific distance + offer + call to action for high relevance."
}
```

---

## Summary

**7 Phases, <100ms total:**

1. Judge sends request
2. API validates
3. Bot composes
4. API returns response
5. Judge scores (5 dimensions)
6. Submission built (30 lines)
7. Validator checks (all pass)

**Result: 24.1/50 average (deterministic baseline)** ✓
