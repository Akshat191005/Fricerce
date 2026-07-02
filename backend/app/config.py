"""
Global configuration and singleton clients.
All API keys are read from environment variables (or .env at project root).
"""
import os
from functools import lru_cache
from pathlib import Path

import boto3
from dotenv import load_dotenv
from groq import Groq
from pinecone import Pinecone

# Load .env from project root (hackon3/) — safe to call multiple times
_ROOT = Path(__file__).parent.parent.parent  # hackon3/
load_dotenv(_ROOT / ".env")
load_dotenv(Path(__file__).parent.parent / ".env")  # backend/.env fallback

# ── Environment Variables ──────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")

AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "frictionless-users")

# Pinecone index name
PINECONE_INDEX_NAME: str = "frictionless-commerce"

# Groq model — Llama 4 Scout: fast MoE (17B active params) with strong
# instruction-following and clean JSON-mode support. Newer/faster than the
# older llama-3.3-70b-versatile, well-suited for low-latency intent parsing.
GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"


# ── Singleton Client Factories ─────────────────────────────────────────────

def get_groq_client() -> Groq:
    """Return a Groq client reading the key fresh each call (supports hot key swaps)."""
    key = os.getenv("GROQ_API_KEY", GROQ_API_KEY)
    return Groq(api_key=key)


@lru_cache(maxsize=1)
def get_pinecone_index():
    """Return a cached Pinecone index client."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(PINECONE_INDEX_NAME)


@lru_cache(maxsize=1)
def get_dynamodb_table():
    """
    Return a cached DynamoDB Table resource.
    On Lambda: use the execution role (no explicit credentials).
    Locally: use the credentials from .env.
    """
    is_lambda = bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

    if is_lambda:
        # Lambda execution role provides credentials automatically
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    else:
        # Local dev — use explicit credentials from .env
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    return dynamodb.Table(DYNAMODB_TABLE_NAME)
