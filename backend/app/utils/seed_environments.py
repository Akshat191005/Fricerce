"""
Seed script: catalog → Pinecone (integrated inference), users → AWS DynamoDB.
Uses Pinecone's HOSTED embedding model (llama-text-embed-v2) so neither local
dev nor Lambda needs torch/sentence-transformers.

Run: python -m app.utils.seed_environments  (from backend/ directory)
"""
import json
import os
import time
from decimal import Decimal
from pathlib import Path

import boto3
from dotenv import load_dotenv
from pinecone import Pinecone

# Load .env from project root (hackon3/)
_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(_ROOT / ".env")
load_dotenv(Path(__file__).parent.parent.parent / ".env")

UTILS_DIR = Path(__file__).parent
SEED_JSON = UTILS_DIR / "seed_data.json"

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "frictionless-users")

# Integrated-inference index (Pinecone hosts the embedding model)
INDEX_NAME = "frictionless-commerce"
EMBED_MODEL = "llama-text-embed-v2"
NAMESPACE = "catalog"


def load_seed_data() -> dict:
    with open(SEED_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_floats_to_decimal(i) for i in obj]
    return obj


def seed_dynamodb(users: dict) -> None:
    if not AWS_ACCESS_KEY_ID:
        raise EnvironmentError("AWS_ACCESS_KEY_ID not set.")

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    for user_id, profile in users.items():
        table.put_item(Item=_floats_to_decimal(profile))
        print(f"  ✅ Written user {user_id}")

    print(f"✅ DynamoDB seeded: {len(users)} user(s)")


def seed_pinecone(catalog: list[dict]) -> None:
    """Recreate index with integrated embedding model, then upsert text records."""
    if not PINECONE_API_KEY:
        raise EnvironmentError("PINECONE_API_KEY not set.")

    pc = Pinecone(api_key=PINECONE_API_KEY)

    existing = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME in existing:
        print(f"🗑️  Deleting existing index '{INDEX_NAME}'...")
        pc.delete_index(INDEX_NAME)
        time.sleep(3)

    print(f"Creating integrated-inference index '{INDEX_NAME}' ({EMBED_MODEL})...")
    pc.create_index_for_model(
        name=INDEX_NAME,
        cloud="aws",
        region="us-east-1",
        embed={
            "model": EMBED_MODEL,
            "field_map": {"text": "chunk_text"},
        },
    )
    print("  Waiting for index to be ready...", end="", flush=True)
    while not pc.describe_index(INDEX_NAME).status.get("ready"):
        print(".", end="", flush=True)
        time.sleep(2)
    print(" ready!")

    index = pc.Index(INDEX_NAME)

    # Build records — 'chunk_text' is what gets embedded; rest is metadata
    records = []
    for item in catalog:
        records.append({
            "_id": item["sku"],
            "chunk_text": f"{item['name']}. {item['description']}",
            "sku": item["sku"],
            "name": item["name"],
            "description": item["description"],
            "price": item["price"],
            "stock_quantity": item["stock_quantity"],
            "delivery_time_hours": item["delivery_time_hours"],
            "category": item["category"],
            "brand": item["brand"],
            "image_url": item["image_url"],
        })

    print(f"Upserting {len(records)} catalog records (Pinecone embeds server-side)...")
    batch_size = 90  # integrated upsert limit is 96/batch
    for i in range(0, len(records), batch_size):
        batch = records[i: i + batch_size]
        index.upsert_records(NAMESPACE, batch)
        print(f"  Upserted batch {i // batch_size + 1} ({len(batch)} records)")

    print(f"✅ Pinecone seeded: {len(records)} records in '{INDEX_NAME}'")


def main() -> None:
    data = load_seed_data()
    seed_dynamodb(data["users"])
    seed_pinecone(data["catalog"])
    print("\n🚀 Seeding complete!")


if __name__ == "__main__":
    main()
