"""
Fast-path DynamoDB service.
Performs O(1) lookups against real AWS DynamoDB to find previously
purchased items matching a product name or SKU.
"""
import asyncio

from app.config import get_dynamodb_table
from app.schemas.core import UnifiedItem


def _match_items_in_user_data(product_name: str, user_data: dict) -> list[UnifiedItem]:
    """Match a single product name against a user's purchase history."""
    results: list[UnifiedItem] = []
    # Normalize: lowercase + replace hyphens/underscores with spaces
    product_name_normalized = product_name.lower().replace("-", " ").replace("_", " ").strip()
    product_words = set(product_name_normalized.split())

    for txn in user_data.get("past_transactions", []):
        for item in txn.get("items_purchased", []):
            item_name_normalized = item["name"].lower().replace("-", " ").replace("_", " ")
            # Match if: full phrase is substring OR any search word appears in item name
            substring_match = product_name_normalized in item_name_normalized
            word_match = any(w in item_name_normalized for w in product_words if len(w) > 3)
            sku_match = product_name.upper() == item["sku"].upper()
            if substring_match or word_match or sku_match:
                results.append(
                    UnifiedItem(
                        sku=item["sku"],
                        name=item["name"],
                        description=item["description"],
                        price=float(item["price"]),
                        stock_quantity=int(item["stock_quantity"]),
                        delivery_time_hours=int(item["delivery_time_hours"]),
                        category=item["category"],
                        brand=item["brand"],
                        image_url=item["image_url"],
                        source_database="dynamodb_history",
                        context_badge=f"Reorder: You bought this on {txn['purchase_date'][:10]}",
                    )
                )

    return results


async def _fetch_user(user_id: str) -> dict | None:
    """Single DynamoDB GetItem by user_id (partition key), run off the event loop."""
    loop = asyncio.get_running_loop()

    def _fetch() -> dict | None:
        table = get_dynamodb_table()
        response = table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        if item:
            txn_count = len(item.get("past_transactions", []))
            print(f"[dynamo] found user {user_id}, {txn_count} transactions")
        else:
            print(f"[dynamo] NO user found for user_id={user_id!r}")
        return item

    return await loop.run_in_executor(None, _fetch)


async def lookup_user_history_multi(
    product_names: list[str],
    user_id: str,
) -> dict[str, list[UnifiedItem]]:
    """
    Fetch the user's record ONCE and match every requested product name
    against their purchase history.

    Returns a dict mapping each product_name -> list of matching UnifiedItems.
    Names with no match map to an empty list (so callers can trigger a
    semantic fallback).
    """
    if not product_names:
        return {}

    user_data = await _fetch_user(user_id)
    if not user_data:
        return {name: [] for name in product_names}

    return {
        name: _match_items_in_user_data(name, user_data)
        for name in product_names
    }


async def lookup_user_history(
    product_name: str,
    user_id: str,
) -> list[UnifiedItem]:
    """
    Backwards-compatible single-name lookup.
    Prefer lookup_user_history_multi when resolving several names at once.
    """
    user_data = await _fetch_user(user_id)
    if not user_data:
        return []
    return _match_items_in_user_data(product_name, user_data)
