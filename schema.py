from pydantic import BaseModel, Field
from typing import List

# --- Extraction Contracts (Input from AI) ---
class ExtractedProduct(BaseModel):
    product_name: str = Field(description="Cleaned text name of the specific item.")
    action_type: str = Field(description="'REORDER' if past purchase is inferred, else 'DISCOVERY'.")

class UnifiedUserIntent(BaseModel):
    cart_type: str = Field(description="'FRICTIONLESS', 'INTENT', or 'MIXED'.")
    extracted_products: List[ExtractedProduct] = Field(default=[])
    abstract_goals: List[str] = Field(default=[])

# --- Database & UI Contracts (Output to Frontend) ---
class CatalogItem(BaseModel):
    sku: str
    name: str
    description: str
    price: float
    stock_quantity: int
    delivery_time_hours: int
    category: str
    brand: str
    image_url: str

class TransactionRecord(BaseModel):
    transaction_id: str
    purchase_date: str
    items_purchased: List[CatalogItem]
    total_amount: float

class UserProfile(BaseModel):
    user_id: str
    full_name: str
    past_transactions: List[TransactionRecord] = Field(default=[])

class UnifiedItem(CatalogItem):
    source_database: str = Field(description="'dynamodb_history' or 'pinecone_semantic'")
    context_badge: str = Field(description="Dynamic string explaining why this item is in the cart.")