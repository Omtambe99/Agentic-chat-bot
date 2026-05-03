# 🤖 Vera — Magicpin AI Merchant Growth Assistant

> **Live Deployment:** [https://magicpin-agentic-chat-bot.onrender.com](https://magicpin-agentic-chat-bot.onrender.com)

Vera is an **LLM-powered agentic chatbot** built for the Magicpin AI Challenge. It acts as magicpin's AI assistant for merchant growth — helping merchants improve listings, run campaigns, and reply faster through intelligent, context-aware WhatsApp-style messaging.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI Server (api.py)           │
│                                                     │
│  /v1/healthz     → Health check                     │
│  /v1/metadata    → Bot identity & model info        │
│  /v1/context     → Receives category/merchant/      │
│                    trigger/customer context          │
│  /v1/tick        → Processes triggers concurrently   │
│  /v1/reply       → Handles merchant replies          │
│  /compose        → Direct message composition        │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │            bot.py (Message Engine)             │  │
│  │                                               │  │
│  │  compose_async() ──► Gemini Flash LLM         │  │
│  │       │                                       │  │
│  │       └──► Deterministic Fallback             │  │
│  │            (if LLM fails or key missing)      │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │    conversation_handlers.py                   │  │
│  │    (Multi-turn conversation state mgmt)       │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **LLM-Powered Composition**: Uses Google Gemini Flash to generate hyper-personalized merchant messages based on four context pillars (Category, Merchant, Trigger, Customer).
- **Deterministic Fallback**: If the LLM is unavailable or the API key is missing, the bot gracefully falls back to a rule-based message engine — ensuring 100% uptime.
- **Async Concurrency**: The `/v1/tick` endpoint processes multiple triggers concurrently using `asyncio.gather`, meeting the <30s latency constraint.
- **Auto-Reply Detection**: Identifies automated/bot replies from merchants (e.g., "Thank you for contacting us") and avoids responding to them.
- **Hostile Message Handling**: Gracefully ends conversations when merchants express frustration or request to stop messaging.
- **Intent Transition**: Detects when a merchant commits ("Ok let's do it") and switches from qualification mode to action mode.
- **Category-Aware Tone**: Adapts voice and vocabulary based on business type (clinical for dentists, warm for salons, operator-to-operator for restaurants).
- **Hinglish Support**: Seamlessly mixes Hindi words into messages when the merchant's language preference includes Hindi.

---

## 🛠️ Tech Stack

| Component         | Technology                          |
|--------------------|-------------------------------------|
| **Web Framework**  | FastAPI + Uvicorn                   |
| **LLM Provider**   | Google Gemini Flash (latest)        |
| **Async HTTP**     | aiohttp                            |
| **Data Validation**| Pydantic v2                         |
| **Secrets Mgmt**   | python-dotenv + Environment Vars    |
| **Deployment**     | Render (Free Tier)                  |
| **Language**        | Python 3.11                         |

---

## 📡 API Endpoints

| Method | Endpoint        | Description                                      |
|--------|-----------------|--------------------------------------------------|
| GET    | `/v1/healthz`   | Health check — returns `{"status": "ok"}`        |
| GET    | `/v1/metadata`  | Returns bot identity, team name, and model info  |
| POST   | `/v1/context`   | Push category/merchant/trigger/customer context   |
| POST   | `/v1/tick`      | Process available triggers and return actions     |
| POST   | `/v1/reply`     | Handle incoming merchant replies                  |
| POST   | `/compose`      | Direct message composition endpoint               |
| GET    | `/docs`         | Interactive Swagger UI documentation              |

---

## 🚀 Live Deployment

The bot is deployed and publicly accessible at:

**🔗 [https://magicpin-agentic-chat-bot.onrender.com](https://magicpin-agentic-chat-bot.onrender.com)**

- **Health Check**: [/v1/healthz](https://magicpin-agentic-chat-bot.onrender.com/v1/healthz)
- **API Docs**: [/docs](https://magicpin-agentic-chat-bot.onrender.com/docs)

---

## 💻 Run Locally

### Prerequisites
- Python 3.10+
- A Google Gemini API key ([Get one here](https://aistudio.google.com/))

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Omtambe99/Agentic-chat-bot.git
   cd Agentic-chat-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key:**
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Start the API server:**
   ```bash
   python api.py
   ```
   The server will start at `http://localhost:8080`.

5. **Test the server (in a separate terminal):**
   ```bash
   python test_api.py
   ```

6. **Run the LLM Judge evaluation:**
   ```bash
   python judge_simulator.py
   ```

### Generate Submission File

```bash
python submission_generator.py
```

This produces `submission.jsonl` in the project root. Validate it with:

```bash
python evaluate_submission.py submission.jsonl
```

---

## 📁 Project Structure

```
├── api.py                    # FastAPI server with all /v1/* endpoints
├── bot.py                    # LLM-powered message engine (core logic)
├── conversation_handlers.py  # Multi-turn conversation state management
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not committed to Git)
├── dataset/                  # Seed data (categories, merchants, triggers)
│   ├── categories/           # Category JSON files
│   ├── merchants_seed.json   # Merchant profiles
│   ├── customers_seed.json   # Customer profiles
│   └── triggers_seed.json    # Trigger definitions
├── expanded/                 # Auto-generated expanded dataset
├── examples/                 # Example compositions
├── submission.jsonl           # Generated submission file
├── submission_generator.py   # Builds submission.jsonl
├── evaluate_submission.py    # Validates JSONL output shape
├── heuristic_judge.py        # Local rubric-style scorer
├── judge_simulator.py        # Full LLM-powered evaluation suite
└── test_api.py               # API endpoint tests
```

---

## 🧠 How the Message Engine Works

The `compose_async()` function in `bot.py` follows this decision flow:

1. **Auto-Reply Check** → If the last merchant message matches known auto-reply patterns, route to a human.
2. **LLM Generation** → Send the four context pillars (Category, Merchant, Trigger, Customer) to Gemini Flash with a carefully engineered system prompt.
3. **Structured Output** → The LLM returns a JSON object with `body`, `cta`, `send_as`, `suppression_key`, and `rationale`.
4. **Fallback** → If the LLM call fails for any reason, fall back to the deterministic `compose_deterministic()` function which uses rule-based logic.

---

## 📊 Evaluation Results

The bot passes all judge simulator scenarios:

| Scenario          | Status |
|-------------------|--------|
| Warmup            | ✅ PASS |
| Auto-Reply Detection | ✅ PASS |
| Intent Transition | ✅ PASS |
| Hostile Handling  | ✅ PASS |

---

## 👤 Team

- **Om Tambe** — [GitHub](https://github.com/Omtambe99)

---

## 📄 License

This project was built for the **Magicpin AI Challenge** hackathon.
