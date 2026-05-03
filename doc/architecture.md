# Vera challenge architecture

## Product goal

Build a deterministic, context-aware WhatsApp message composer that can handle merchant-facing and customer-facing flows for the magicpin Vera challenge.

## Inputs

- `CategoryContext`: category voice, offers, peer benchmarks, digest items, seasonal beats, and trend signals.
- `MerchantContext`: identity, subscription, performance, offers, conversation history, customer aggregates, and derived signals.
- `TriggerContext`: the event that explains why this message is being sent right now.
- `CustomerContext` (optional): used when the merchant is messaging one of their own customers.

## Core pipeline

1. Load the expanded dataset from `expanded/`.
2. Pick a `(category, merchant, trigger, customer?)` tuple.
3. Call `bot.compose(...)`.
4. Validate the result shape and constraints.
5. Write the output to JSONL for submission.

## Message design rules

- Prefer concrete facts from the supplied contexts.
- Use the merchant's voice, category vocabulary, and language preference.
- Detect clear intent and route immediately instead of re-qualifying.
- Detect common auto-replies and stop wasting turns.
- Keep one primary CTA.
- Never invent offers, research, or merchant state.

## Folder responsibilities

- `dataset/generate_dataset.py`: expands seed data into the full contest dataset.
- `bot.py`: rule-based composer.
- `submission_generator.py`: builds the 30-line submission JSONL.
- `evaluate_submission.py`: local sanity checks for constraint compliance.

## Recommended next upgrade

- Replace the fallback rule engine with a prompt+retrieval layer, but keep the same contract and validations.
