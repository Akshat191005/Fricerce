// Mirrors backend/app/schemas/core.py Pydantic models exactly

export interface CatalogItem {
  sku: string;
  name: string;
  description: string;
  price: number;
  stock_quantity: number;
  delivery_time_hours: number;
  category: string;
  brand: string;
  image_url: string;
}

export interface TransactionRecord {
  transaction_id: string;
  purchase_date: string;
  items_purchased: CatalogItem[];
  total_amount: number;
}

export interface UserProfile {
  user_id: string;
  full_name: string;
  past_transactions: TransactionRecord[];
}

// Extends CatalogItem with dual-path routing metadata
export interface UnifiedItem extends CatalogItem {
  source_database: "dynamodb_history" | "pinecone_semantic";
  context_badge: string;
}

export interface ExtractedProduct {
  product_name: string;
  action_type: "REORDER" | "DISCOVERY";
}

export interface UnifiedUserIntent {
  cart_type: "FRICTIONLESS" | "INTENT" | "MIXED";
  extracted_products: ExtractedProduct[];
  abstract_goals: string[];
}

// SSE stream response shape
export interface ChatRequest {
  prompt: string;
  user_id: string;
  urgent?: boolean;
}
