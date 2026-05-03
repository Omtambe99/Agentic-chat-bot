Product spec: Vera challenge minimal plan

Goal

- Build a deterministic, rule-based baseline `bot.py` that composes merchant/customer WhatsApp messages from the 4-context input and meets contest constraints.

Success metrics (align to judge rubric)

- Specificity: include at least one verifiable fact in 80% of messages.
- Category fit: use category `offer_catalog` or `voice` tokens when available.
- Merchant fit: reference `merchant.performance` or `merchant.offers` when present.
- Trigger relevance: explicitly mention trigger.reason and urgency in message rationale.
- Engagement compulsion: 60% of messages should use one compulsion lever (peer stat, loss framing, curiosity).

Phase 1 deliverables

- `bot.py` deterministic composer (rule-based baseline).
- `submission.jsonl` generator script: `submission_generator.py`.
- README with run instructions and rationale.

Next phases

- Implement LLM-backed composer with retrieval-augmented prompt templates.
- Improve auto-reply detection and multi-turn handlers.
- Add evaluation harness that scores messages using the judge LLM (local or API).
