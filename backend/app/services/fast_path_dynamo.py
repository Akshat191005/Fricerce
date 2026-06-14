"""
Fast-path DynamoDB service.
Performs O(1) lookups against real AWS DynamoDB to find previously
purchased items matching a product name or SKU.
"""
import asyncio
from app.config import get_dynamodb_table
from app.schemas.core import UnifiedItem


async def lookup_user_history(
    product_name: str,
    user_id: str,
) -> list[UnifiedItem]:
    """
    O(1) DynamoDB GetItem by user_id (partition key).
    Searches past_transactions for items matching product_name
    (case-insensitive partial match on name, or exact SKU match).
    Returns matching UnifiedItems tagged as dynamodb_history.
    """
    loop = asyncio.get_event_loop()

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

    user_data = await loop.run_in_executor(None, _fetch)
    if not user_data:
        return []

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
            print(f"[dynamo] checking '{item['name']}' against '{product_name_normalized}': match={substring_match or word_match or sku_match}")
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
