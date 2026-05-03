# API Deployment & Usage Guide

## Running the API

### Local development (synchronous)

```bash
python api.py
```

This starts Uvicorn on `http://localhost:8080`.

### Production-grade (with Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 --worker-class uvicorn.workers.UvicornWorker api:app
```

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
```

## API Endpoints

### `/health` (GET)

Health check endpoint. Returns `{"status": "healthy", "message": "Vera API is running"}`.

```bash
curl http://localhost:8080/health
```

### `/compose` (POST)

Compose a WhatsApp message from contexts.

**Request body:**

```json
{
  "category": { ...CategoryContext... },
  "merchant": { ...MerchantContext... },
  "trigger": { ...TriggerContext... },
  "customer": { ...CustomerContext... } // optional
}
```

**Response:**

```json
{
  "body": "The WhatsApp message text",
  "cta": "YES/STOP|open_ended|none",
  "send_as": "vera|merchant_on_behalf",
  "suppression_key": "dedup_key",
  "rationale": "Why this message was composed"
}
```

**Example:**

```bash
curl -X POST http://localhost:8080/compose \
  -H "Content-Type: application/json" \
  -d '{
    "category": {"slug": "dentists", "voice": {}},
    "merchant": {"merchant_id": "m_001", "identity": {"name": "Dr. Meera"}},
    "trigger": {"kind": "research_digest", "payload": {}},
    "customer": null
  }'
```

### `/docs` (GET)

Interactive Swagger API documentation (auto-generated).

### `/openapi.json` (GET)

OpenAPI schema in JSON format.

## Testing the API

```bash
python test_api.py
```

This validates the `/health` and `/compose` endpoints with real data from the expanded dataset.

## Integration with Judge Simulator

The judge simulator (`judge_simulator.py`) can call this API by setting:

```python
BOT_URL = "http://localhost:8080"
```

Then configure your LLM provider and run the judge to evaluate your bot's responses across the challenge rubric.

## Performance & Scaling

- **Latency**: Single compose call typically completes in <100ms on modern hardware
- **Concurrency**: Uvicorn handles up to 100s of concurrent requests with default settings
- **Scaling**: Use multiple workers or container orchestration (Kubernetes) for high throughput

## Environment Variables

None required. All configuration is via code in `api.py` and `bot.py`.
