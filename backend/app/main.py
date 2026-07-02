"""
FastAPI application — core routing and SSE streaming endpoint.
"""
import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.schemas.core import UnifiedItem
from app.services.llm_orchestrator import parse_user_intent
from app.services.fast_path_dynamo import lookup_user_history_multi
from app.services.slow_path_pinecone import search_by_goals, search_by_goals_map

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Frictionless Commerce API",
    description="Ultra-low-latency dual-path e-commerce AI copilot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "USER#123"
    urgent: bool = False


def _sse_event(item: UnifiedItem) -> str:
    return f"data: {item.model_dump_json()}\n\n"


async def _compute_results(request: ChatRequest) -> list[UnifiedItem]:
    """Core logic — returns the final ranked, filtered list of items."""
    # Step 1: Parse intent
    logger.info(f"[intent] parsing prompt: {request.prompt!r}")
    intent = await parse_user_intent(request.prompt)
    logger.info(f"[intent] cart_type={intent.cart_type}, "
                f"products={[p.product_name for p in intent.extracted_products]}, "
                f"goals={intent.abstract_goals}")

    # Step 2: Build tasks
    reorder_names = [
        p.product_name for p in intent.extracted_products
        if p.action_type == "REORDER"
    ]
    discovery_names = [
        p.product_name for p in intent.extracted_products
        if p.action_type == "DISCOVERY"
    ]
    # Deduplicate goals
    seen_goals: set[str] = set()
    all_goals: list[str] = []
    for g in intent.abstract_goals + discovery_names:
        g_lower = g.lower().strip()
        if g_lower not in seen_goals:
            seen_goals.add(g_lower)
            all_goals.append(g)

    logger.info(f"[routing] reorders={reorder_names}, goals={all_goals}")

    # Step 3: Run all retrieval concurrently in a single round-trip:
    #   - dynamo_map: purchase-history matches for each reorder name (1 GetItem total)
    #   - slow_results: semantic results for discovery goals
    #   - reorder_semantic_map: semantic results per reorder name, used as a
    #     fallback so a REORDER item that isn't in the user's history still
    #     surfaces a relevant product instead of returning nothing.
    dynamo_map, slow_results, reorder_semantic_map = await asyncio.gather(
        lookup_user_history_multi(reorder_names, request.user_id),
        search_by_goals(all_goals),
        search_by_goals_map(reorder_names),
    )

    fast_results: list[UnifiedItem] = []
    fallback_count = 0
    for name in reorder_names:
        history_hits = dynamo_map.get(name, [])
        if history_hits:
            fast_results.extend(history_hits)
        else:
            # No purchase history for this item — fall back to semantic search
            # so the user still gets a relevant match.
            for item in reorder_semantic_map.get(name, []):
                fallback_count += 1
                fast_results.append(item.model_copy(update={
                    "context_badge": f"Suggested match for '{name}'",
                }))

    logger.info(f"[results] fast={len(fast_results)} "
                f"(history + {fallback_count} semantic fallback), slow={len(slow_results)}")

    # Step 4: Urgent mode
    URGENT_MAX_HOURS = 12
    if request.urgent:
        effective_max_delivery = min(
            intent.max_delivery_hours if intent.max_delivery_hours is not None else URGENT_MAX_HOURS,
            URGENT_MAX_HOURS,
        )
    else:
        effective_max_delivery = intent.max_delivery_hours

    max_budget = intent.max_budget
    exclusions = [e.lower() for e in (intent.exclusions or [])]
    logger.info(f"[filters] max_budget={max_budget}, max_delivery_hours={effective_max_delivery}, exclusions={exclusions}, urgent={request.urgent}")

    def _passes_filters(item: UnifiedItem) -> bool:
        if max_budget is not None and item.price > max_budget:
            return False
        if effective_max_delivery is not None and item.delivery_time_hours > effective_max_delivery:
            return False
        if exclusions:
            searchable = f"{item.name} {item.description}".lower()
            if any(exc in searchable for exc in exclusions):
                return False
        return True

    def _apply_urgent_badge(item: UnifiedItem) -> UnifiedItem:
        if request.urgent and not item.context_badge.startswith("⚡"):
            return item.model_copy(update={
                "context_badge": f"⚡ Fast Delivery ({item.delivery_time_hours}h) · {item.context_badge}"
            })
        return item

    # Step 5: Collect and filter
    all_items: list[UnifiedItem] = []
    seen_skus: set[str] = set()
    for item in fast_results + slow_results:
        if item.sku not in seen_skus and _passes_filters(item):
            seen_skus.add(item.sku)
            all_items.append(_apply_urgent_badge(item))

    # Step 6: Smart re-ranking
    mentioned_terms = set()
    for p in intent.extracted_products:
        for word in p.product_name.lower().split():
            if len(word) > 2:
                mentioned_terms.add(word)
    for goal in intent.abstract_goals:
        for word in goal.lower().split():
            if len(word) > 3:
                mentioned_terms.add(word)

    def _relevance_score(item: UnifiedItem) -> tuple:
        name_lower = item.name.lower()
        desc_lower = item.description.lower()
        if item.source_database == "dynamodb_history":
            tier = 0
        elif any(term in name_lower for term in mentioned_terms):
            tier = 1
        elif any(term in desc_lower for term in mentioned_terms):
            tier = 2
        else:
            tier = 3
        delivery = item.delivery_time_hours if request.urgent else 0
        return (tier, delivery)

    all_items.sort(key=_relevance_score)
    return all_items


async def _stream_results(request: ChatRequest) -> AsyncGenerator[str, None]:
    try:
        items = await _compute_results(request)
        for item in items:
            yield _sse_event(item)
    except Exception as exc:
        logger.exception(f"[error] {exc}")
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


@app.post("/api/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """
    SSE streaming endpoint — works locally (uvicorn).
    Streams UnifiedItem results as Server-Sent Events.
    """
    return StreamingResponse(
        _stream_results(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat/batch")
async def chat_batch(request: ChatRequest) -> dict:
    """
    Non-streaming JSON endpoint — works through API Gateway / Lambda.
    Returns all results at once as a JSON array.
    """
    try:
        items = await _compute_results(request)
        return {"items": [item.model_dump() for item in items]}
    except Exception as exc:
        logger.exception(f"[error] {exc}")
        return {"items": [], "error": str(exc)}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
