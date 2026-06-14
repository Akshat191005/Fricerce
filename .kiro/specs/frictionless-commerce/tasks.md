# Frictionless Commerce – Tasks

## Phase 1: Data Contracts

- [x] 1 Create backend Pydantic schemas and frontend TypeScript interfaces
  - [x] 1.1 Create `backend/app/schemas/__init__.py`
  - [x] 1.2 Create `backend/app/schemas/core.py` with CatalogItem, TransactionRecord, UserProfile, UnifiedItem, ExtractedProduct, UnifiedUserIntent
  - [x] 1.3 Create `frontend/src/types/index.ts` with matching TypeScript interfaces

## Phase 2: Seed Data & Environment

- [x] 2 Create seed data utilities
  - [x] 2.1 Create `backend/app/utils/seed_environments.py` that embeds catalog items with langchain_huggingface and upserts to Pinecone, saves user profile to mock_dynamodb.json
  - [x] 2.2 Create `backend/app/utils/__init__.py`

## Phase 3: Dual-Path Database Services

- [x] 3 Create database service modules
  - [x] 3.1 Create `backend/app/services/__init__.py`
  - [x] 3.2 Create `backend/app/services/fast_path_dynamo.py` with async O(1) mock_dynamodb.json lookup
  - [x] 3.3 Create `backend/app/services/slow_path_pinecone.py` with async Pinecone vector search

## Phase 4: AI Orchestration & API

- [x] 4 Create backend API and orchestration layer
  - [x] 4.1 Create `backend/app/config.py` with singleton clients
  - [x] 4.2 Create `backend/app/services/llm_orchestrator.py` using google-genai SDK with structured output
  - [x] 4.3 Create `backend/app/__init__.py`
  - [x] 4.4 Create `backend/app/main.py` with FastAPI SSE endpoint using asyncio.gather
  - [x] 4.5 Create `backend/lambda_handler.py` with Mangum wrapper
  - [x] 4.6 Create `backend/requirements.txt`

## Phase 5: Reactive Next.js Frontend

- [x] 5 Build Next.js frontend
  - [x] 5.1 Initialize Next.js project with TypeScript and Tailwind at `frontend/`
  - [x] 5.2 Create `frontend/src/types/index.ts`
  - [x] 5.3 Create `frontend/src/store/useCartStore.ts` with Zustand
  - [x] 5.4 Create `frontend/src/components/PromptBar.tsx`
  - [x] 5.5 Create `frontend/src/components/ProductCard.tsx`
  - [x] 5.6 Create `frontend/src/components/SolutionCart.tsx`
  - [x] 5.7 Create `frontend/src/app/page.tsx` and `layout.tsx`
  - [x] 5.8 Create `frontend/src/app/globals.css`
  - [x] 5.9 Create `frontend/tailwind.config.ts` and `frontend/tsconfig.json`
  - [x] 5.10 Create `frontend/package.json`
