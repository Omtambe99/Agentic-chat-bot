Vera (magicpin) — Starter submission

What this scaffold provides

- `bot.py`: deterministic baseline `compose()` function that follows challenge constraints.
- `submission_generator.py`: builds `submission.jsonl` by running `bot.compose` over dataset triggers.
- `api.py`: FastAPI HTTP server that exposes `compose()` and the judge-facing `/v1/*` endpoints.
- `evaluate_submission.py`: validates the JSONL output shape.
- `heuristic_judge.py`: local rubric-style scorer for the generated messages.
- `product_spec.md`: short product spec and success metrics.
- `API_DEPLOYMENT.md`: deployment guide and endpoint documentation.

Run locally

1. Ensure Python 3.10+ is installed.
2. The checked-in seed files in `dataset/` are enough; the generator will create `expanded/` automatically.
3. Generate the submission JSONL:

```bash
python submission_generator.py
```

This will produce `submission.jsonl` in the project root.

Optional checks:

```bash
python evaluate_submission.py submission.jsonl
python heuristic_judge.py
```

Run the API server:

```bash
python api.py
```

Then test it in another terminal:

```bash
python test_api.py
```

The API will be available at `http://localhost:8080/docs` for interactive exploration.

Next steps

- Tune message quality against heuristic scorer scores to improve specificity and trigger relevance.
- Add LLM-based generation layer for higher-quality outputs.
- Implement multi-turn conversation handling and state management.
