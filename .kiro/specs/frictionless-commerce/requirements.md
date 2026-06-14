# Frictionless Commerce – Requirements

## Overview
An ultra-low-latency, dual-path e-commerce AI copilot. Users enter a natural language prompt; the system uses Gemini (Structured Outputs) to extract explicit reorders and abstract discovery intents, then executes DynamoDB and Pinecone lookups concurrently, streaming results back via SSE.

## Requirements

### R1 – Data Contracts
- R1.1: Backend Pydantic schemas: CatalogItem, TransactionRecord, UserProfile, UnifiedItem, ExtractedProduct, UnifiedUserIntent
- R1.2: Frontend TypeScript interfaces mirroring all backend schemas exactly
- R1.3: UnifiedItem extends CatalogItem with `source_database` and `context_badge` fields
- R1.4: UnifiedUserIntent contains `extracted_products` (List[ExtractedProduct]) and `abstract_goals` (List[str])

### R2 – Seed Data & Environment Setup
- R2.1: seed_data.json with 5+ catalog items and one user (USER#123) with past transactions
- R2.2: seed_environments.py embeds catalog items using langchain_huggingface (all-MiniLM-L6-v2) and upserts to Pinecone
- R2.3: seed_environments.py saves user profile to mock_dynamodb.json

### R3 – Dual-Path Database Services
- R3.1: fast_path_dynamo.py performs O(1) lookup in mock_dynamodb.json by item name/SKU + user ID, returns UnifiedItem with source_database="dynamodb_history"
- R3.2: slow_path_pinecone.py generates embedding for a vague goal, queries Pinecone, returns List[UnifiedItem] with source_database="pinecone_semantic"
- R3.3: Both services are async

### R4 – AI Orchestration & API
- R4.1: llm_orchestrator.py uses google-genai SDK with Gemini, enforces UnifiedUserIntent structured output
- R4.2: main.py FastAPI app with POST /api/chat endpoint
- R4.3: /api/chat calls orchestrator then asyncio.gather() for concurrent dual-path lookups
- R4.4: Results streamed as Server-Sent Events via StreamingResponse
- R4.5: lambda_handler.py wraps FastAPI with Mangum for AWS Lambda / API Gateway

### R5 – Reactive Next.js Frontend
- R5.1: useCartStore.ts Zustand store handles SSE chunks, appends items to array
- R5.2: PromptBar.tsx auto-expanding textarea with Urgent Toggle
- R5.3: SolutionCart.tsx renders streaming items without blocking UI
- R5.4: ProductCard.tsx displays item with context_badge highlighted
- R5.5: page.tsx root layout: PromptBar at top, SolutionCart below
