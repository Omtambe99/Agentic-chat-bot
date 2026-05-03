# Vera Challenge — Submission Summary

## Overview

**Approach:** Rule-based deterministic message composer with heuristic local scoring.  
**Architecture:** 4-context model → trigger classification → template-based composition → WhatsApp message generation  
**Evaluation Score (Heuristic):** 24.1/50 average across 5 dimensions

## Submission Contents

| File                      | Purpose                                                                                                                       |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `bot.py`                  | Core composer function: deterministic WhatsApp message generation from 4-context inputs                                       |
| `submission.jsonl`        | 30 test cases (JSONL format): each line is {test_id, body, cta, send_as, suppression_key, rationale}                          |
| `api.py`                  | FastAPI HTTP server wrapping bot.compose() for judge simulator integration                                                    |
| `submission_generator.py` | Builds submission.jsonl by running bot.compose over expanded dataset                                                          |
| `evaluate_submission.py`  | Validates JSONL output shape (required keys, value types, length constraints)                                                 |
| `heuristic_judge.py`      | Local rubric scorer: dimension-by-dimension analysis (specificity, category fit, merchant fit, trigger relevance, engagement) |
| `dataset/`                | Seed data: customers_seed.json, merchants_seed.json, triggers_seed.json, categories/                                          |
| `expanded/`               | Auto-expanded test data (50 merchants, 200 customers, 100 triggers)                                                           |

## Score Breakdown

**Final Evaluation (Heuristic Judge):**

```json
{
  "average_total": 24.1,
  "average_specificity": 3.13,
  "average_category_fit": 6.13,
  "average_merchant_fit": 4.7,
  "average_trigger_relevance": 4.8,
  "average_engagement": 5.33
}
```

**Dimension Insights:**

- **Trigger Relevance (4.8/10):** Optimized with keywords ("heads-up", "due", "upcoming") to explain "why now"
- **Category Fit (6.13/10):** Solid — category voice applied consistently
- **Engagement (5.33/10):** Strong CTAs (YES/STOP, open_ended) for merchant/customer action
- **Specificity (3.13/10):** Baseline — includes numbers/amounts where data provides them
- **Merchant Fit (4.7/10):** Personalized with salutation & merchant name

## Quick Start

1. Generate 30-line submission:

```bash
python submission_generator.py
```

2. Validate output:

```bash
python evaluate_submission.py submission.jsonl
python heuristic_judge.py
```

3. Start API service (for judge integration):

```bash
python api.py
```

API will be available at `http://localhost:8080` with auto-docs at `/docs`.

## Key Design Decisions

### 1. Deterministic vs. LLM-based

- **Why deterministic:** Challenge constraint is <30s per-call; rule-based templates meet this easily without LLM latency/cost
- **Tradeoff:** Lower quality than LLM but fully deterministic and reproducible

### 2. Trigger Classification

Triggers are categorized into 15+ types:

- Merchant-facing: research_digest, regulation_change, perf_spike/dip, renewal_due, active_planning_intent, dormant_with_vera, festival_upcoming, review_theme_emerged, competitor_opened
- Customer-facing: recall_due, appointment_tomorrow, trial_followup
- Auto-reply detection & fallback

### 3. Message Design Constraints Honored

- ✅ No auto-replies sent (early termination with routing message)
- ✅ No fabrication (only merchant/trigger/category data used)
- ✅ Single primary CTA (YES/STOP or open_ended or none)
- ✅ Specificity over generic (extracted numbers, dates, amounts where available)
- ✅ Deterministic output (same input → same output guaranteed)

### 4. Heuristic Scoring

Local judge evaluates based on:

- **Specificity:** Numbers (+4), rupees (+2), dates (+2), length >80 (+1)
- **Category Fit:** Category mentions (+2), category-specific keywords (+2)
- **Merchant Fit:** Personalization ("Hi", "your", "dashboard") (+5 total)
- **Trigger Relevance:** Keywords ("heads-up", "due", "upcoming") (+4), CTA type (+2)
- **Engagement:** CTA strength (+4), action prompts (+4), urgency language (+2)

## Next Steps for Improvement

1. **Add LLM layer** for higher quality (GPT, Claude, etc.) with caching for <30s latency
2. **Multi-turn conversation handling** (conversation_handlers.py) for context memory across turns
3. **A/B testing variants** of CTAs and messaging to optimize per-merchant
4. **Category-specific ML** (e.g., dentist-specific triggers vs. restaurant triggers)
5. **Customer preference learning** from conversation history (avoid over-triggering, timing optimization)

## Challenge Integration

The judge simulator will:

1. Load merchants, customers, triggers from `dataset/`
2. Call the API at `POST /compose` with structured context
3. Receive {body, cta, send_as, suppression_key, rationale}
4. Evaluate against 5-dimension rubric (50pt max)
5. Return scores

## Files Status

✅ All submission files validated and ready  
✅ API service deployable immediately  
✅ Submission.jsonl passes format validation  
✅ 100% deterministic (reproducible outputs)  
✅ No external dependencies beyond FastAPI + Uvicorn

---

**Submission Date:** May 2, 2026  
**Format:** 30-line JSONL + Python service  
**Deployment:** Single `python api.py` command
