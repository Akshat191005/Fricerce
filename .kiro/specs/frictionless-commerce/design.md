# Frictionless Commerce – Design

## Architecture

### Dual-Path Flow
```
User Prompt → POST /api/chat
  → LLM Orchestrator (Gemini Structured Output)
      → UnifiedUserIntent { extracted_products, abstract_goals }
  → asyncio.gather(
      fast_path_dynamo(reorder_items, user_id),   # O(1) mock_dynamodb.json lookup
      slow_path_pinecone(abstract_goals)           # Vector search via Pinecone
    )
  → StreamingResponse (SSE) → Zustand store → React UI
```

### Backend Structure
- `config.py` – singleton clients (boto3/mock, Pinecone, Gemini)
- `schemas/core.py` – Pydantic models (single source of truth)
- `services/llm_orchestrator.py` – Gemini call with response_schema
- `services/fast_path_dynamo.py` – JSON file mock of DynamoDB
- `services/slow_path_pinecone.py` – Pinecone vector query
- `main.py` – FastAPI SSE endpoint
- `lambda_handler.py` – Mangum wrapper

### Frontend Structure
- `types/index.ts` – TypeScript mirrors of Pydantic models
- `store/useCartStore.ts` – Zustand: items[], isLoading, addItem, reset
- `components/PromptBar.tsx` – textarea + urgent toggle
- `components/SolutionCart.tsx` – SSE consumer + item grid
- `components/ProductCard.tsx` – card with context_badge badge
- `app/page.tsx` – root page composition

### SSE Protocol
Each SSE event: `data: <JSON UnifiedItem>\n\n`
Terminal event: `data: [DONE]\n\n`

### Key Design Decisions
- mock_dynamodb.json replaces real DynamoDB for local dev / hackathon demo
- Pinecone Serverless used for semantic search
- all-MiniLM-L6-v2 via langchain_huggingface for embeddings (free, fast)
- Gemini `response_mime_type="application/json"` + `response_schema` for strict output
