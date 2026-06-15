<div align="center">

# ⚡ Fricerce — Frictionless Commerce

### One sentence. Zero friction. Instant cart.

An AI shopping copilot that turns a single plain English request into a ready-to-checkout cart blending **instant reorders** from your purchase history with **AI powered discovery** of new products, all in parallel.

[![Live App](https://img.shields.io/badge/Live%20App-fricerce.vercel.app-orange?style=for-the-badge)](https://fricerce.vercel.app/)
&nbsp;
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
&nbsp;
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.13-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
&nbsp;
[![AWS](https://img.shields.io/badge/AWS-Lambda%20%2B%20DynamoDB-FF9900?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com/)

*Built for **HackOn with Amazon** · Theme: Amazon Now – Reimagining Urgent Shopping · Team Akatsuki*

</div>

---

## 🎯 The Problem

E-commerce search is broken. It forces shoppers to squeeze two fundamentally different intents into one rigid keyword box:

- **Reordering** something they already buy ("my usual coffee pods")
- **Discovering** something for a vague need ("gear for a camping trip")

Treating both the same way creates friction, decision fatigue, and abandoned carts — cart abandonment sits around **70%** industry-wide. Every extra step between intent and checkout costs conversion.

## 💡 The Solution

**Fricerce** treats your natural language as the ultimate search index. You describe what you need in one sentence, and it instantly assembles your cart.

> *"Reorder my mouse and find something for my camping trip under $100, by tomorrow"*

The core insight: **reorders and discovery are different retrieval problems and should run on different engines, in parallel.** An LLM routes a single prompt across two paths simultaneously, then merges the results into one unified, explainable cart.

---

## ✨ Key Features

| Feature | What it does |
|---------|-------------|
| 🧠 **Zero-Shot Intent Parsing** | Groq (`llama-3.3-70b`) dissects one sentence into reorder intents, semantic goals, budget caps, delivery deadlines, and exclusions |
| 🛣️ **Dual-Path Retrieval Engine** | Exact reorders from **DynamoDB** (O(1)) run concurrently with semantic discovery from **Pinecone** vector search |
| ⚡ **Urgent Mode** | One toggle re-ranks the cart around speed caps delivery windows and surfaces the fastest arriving items first |
| 🏷️ **Explainable Cart** | Every item shows *why* it's there: a reorder from history, or an AI match for your goal |
| 🎯 **Smart Constraints** | Auto-applies budget limits, delivery deadlines, and exclusions ("not red", "no leather") parsed from plain text |
| 📡 **Live Streaming** | Results stream in progressively via Server Sent Events for instant perceived speed |

---

## 🏗️ Architecture

```
          ┌──────────────────────────────────────────────┐
          │   Next.js 14 Frontend (Vercel)               │
          │   PromptBar → Zustand store → SolutionCart   │
          └───────────────┬──────────────────────────────┘
                          │  POST /api/chat        (SSE — local)
                          │  POST /api/chat/batch  (JSON — Lambda)
                          ▼
          ┌──────────────────────────────────────────────┐
          │   FastAPI Backend  (AWS Lambda + API Gateway) │
          │                                               │
          │   1. parse_user_intent()  ──► Groq LLM        │
          │   2. split REORDER / DISCOVERY                │
          │   3. asyncio.gather (concurrent):             │
          │        ├─ FAST  ──► DynamoDB  (O(1) GetItem)  │
          │        └─ SLOW  ──► Pinecone  (O(log N) HNSW) │
          │   4. filter (budget / delivery / exclusions)  │
          │   5. dedupe + tiered re-ranking               │
          └───────────────┬───────────────┬───────────────┘
                          ▼               ▼
                    ┌──────────┐    ┌──────────────────┐
                    │ DynamoDB │    │     Pinecone     │
                    │ user     │    │ catalog vectors  │
                    │ history  │    │ (llama-text-     │
                    │          │    │  embed-v2)       │
                    └──────────┘    └──────────────────┘
```

### Core Algorithm — Concurrent Dual-Path Fetch

- **Fast Path:** `O(1)` DynamoDB `GetItem` on the user partition key → match against purchase history.
- **Slow Path:** `O(log N)` Pinecone HNSW vector search, one query per goal, round robin interleaved.
- Both launch together via Python's `asyncio.gather`, so total latency is bounded by the **slower** path not the sum.
- A **Smart Re-ranking** pass (`O(M log M)`) sorts items by origin tier (history > semantic), term overlap, and delivery urgency.

---

## 🧰 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Zustand, Clerk | Responsive streaming UI with modern state management |
| **Backend** | FastAPI (Python 3.13), Pydantic | High-performance async routing + native SSE streaming |
| **AI / LLM** | Groq `llama-3.3-70b-versatile` (JSON mode) | Ultra-fast structured intent parsing |
| **Data / ML** | AWS DynamoDB, Pinecone (integrated `llama-text-embed-v2`) | Instant history lookups + server-side semantic search |
| **Infra** | AWS Lambda, API Gateway, SAM, Mangum, Vercel | Serverless, scale-to-zero, globally distributed |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.13
- API keys: **Groq**, **Pinecone**, and **AWS** credentials (with DynamoDB access)

### 1. Clone

```bash
git clone https://github.com/Akshat191005/Fricerce.git
cd Fricerce
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=ap-southeast-2
DYNAMODB_TABLE_NAME=frictionless-users
```

And `frontend/.env.local` for the frontend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# Seed DynamoDB (users) + Pinecone (catalog)
python -m app.utils.seed_environments

# Run the API (hot-reload)
uvicorn app.main:app --reload --port 8000
```

API runs at `http://localhost:8000` · docs at `http://localhost:8000/docs`

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`

---

## ☁️ Deployment

**Backend (AWS SAM):**

```bash
cd backend
sam build
sam deploy --guided    # first time — sets API keys & region
# sam deploy           # subsequent deploys
```

The output `ApiUrl` becomes your frontend's `NEXT_PUBLIC_API_URL`.

> **Note:** On Lambda + API Gateway the frontend auto-switches to the non-streaming `/api/chat/batch` endpoint (API Gateway can't stream SSE). Local dev uses the streaming `/api/chat` endpoint.

**Frontend (Vercel):** Connect the `frontend/` directory and set `NEXT_PUBLIC_API_URL` to your deployed API URL.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Streams `UnifiedItem` results as Server-Sent Events |
| `POST` | `/api/chat/batch` | Returns all results at once as JSON (Lambda-friendly) |
| `GET` | `/health` | Health check |

**Request body:**

```json
{
  "prompt": "reorder my mouse and find camping gear under $100",
  "user_id": "USER#123",
  "urgent": false
}
```

---

## 🔭 Future Vision

- **0–3 mo** — Real-time inventory API integration with live seller databases
- **3–6 mo** — Multimodal & voice search (snap a photo, or ask Alexa)
- **6–12 mo** — Predictive auto-purchasing of staples before you run out

**Multi-segment expansion:** B2B procurement · Healthcare prescription refills · Grocery / quick-commerce.

---

## 👥 Team Akatsuki

| Name | Role |
|------|------|
| Bhavya Kalal | Full Stack Developer |
| Akshat Singhvi | ML Engineer |
| Rashika Tyagi | Designer |

*Thapar Institute of Engineering and Technology, Patiala*

---

## 🔗 Links

**Live App:** https://fricerce.vercel.app/ · **GitHub:** https://github.com/Akshat191005/Fricerce

<div align="center">

*Built with ⚡ for HackOn with Amazon*

</div>
