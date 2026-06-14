"""
Slow-path Pinecone service — uses Pinecone Integrated Inference.
Pinecone hosts the embedding model (llama-text-embed-v2), so we just send
the text query and Pinecone embeds + searches server-side.
No torch, no HuggingFace — works identically on local and Lambda.
"""
import asyncio
from functools import lru_cache

from pinecone import Pinecone

from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from app.schemas.core import UnifiedItem

INDEX_NAME = PINECONE_INDEX_NAME
NAMESPACE = "catalog"
TOP_K = 3


@lru_cache(maxsize=1)
def _get_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(INDEX_NAME)


async def search_by_goal(goal: str, top_k: int = TOP_K) -> list[UnifiedItem]:
    try:
        loop = asyncio.get_event_loop()

        def _query() -> list:
            index = _get_index()
            results = index.search(
                namespace=NAMESPACE,
                query={"inputs": {"text": goal}, "top_k": top_k},
                fields=[
                    "sku", "name", "description", "price", "stock_quantity",
                    "delivery_time_hours", "category", "brand", "image_url",
                ],
            )
            return results.get("result", {}).get("hits", [])

        hits = await loop.run_in_executor(None, _query)

        unified_items: list[UnifiedItem] = []
        for hit in hits:
            fields = hit.get("fields", {})
            score = hit.get("_score", 0.0)
            unified_items.append(
                UnifiedItem(
                    sku=fields.get("sku", hit.get("_id", "")),
                    name=fields.get("name", ""),
                    description=fields.get("description", ""),
                    price=float(fields.get("price", 0.0)),
                    stock_quantity=int(fields.get("stock_quantity", 0)),
                    delivery_time_hours=int(fields.get("delivery_time_hours", 0)),
                    category=fields.get("category", ""),
                    brand=fields.get("brand", ""),
                    image_url=fields.get("image_url", ""),
                    source_database="pinecone_semantic",
                    context_badge=f"Discovered: Matches your goal '{goal}' ({score:.0%} similarity)",
                )
            )
        return unified_items

    except Exception as exc:
        print(f"[slow_path_pinecone] Error: {exc}")
        return []


async def search_by_goals(goals: list[str]) -> list[UnifiedItem]:
    if not goals:
        return []

    tasks = [search_by_goal(goal) for goal in goals]
    results_per_goal: list[list[UnifiedItem]] = list(await asyncio.gather(*tasks))

    # Round-robin interleave so each goal's top match comes first
    seen: set[str] = set()
    unified: list[UnifiedItem] = []
    max_len = max((len(r) for r in results_per_goal), default=0)

    for round_idx in range(max_len):
        for goal_results in results_per_goal:
            if round_idx < len(goal_results):
                item = goal_results[round_idx]
                if item.sku not in seen:
                    seen.add(item.sku)
                    unified.append(item)

    return unified
