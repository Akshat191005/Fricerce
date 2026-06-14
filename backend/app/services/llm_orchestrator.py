"""
LLM Orchestrator: calls Groq (llama-3.3-70b-versatile) with JSON mode
to parse a user prompt into a UnifiedUserIntent.
"""
import asyncio

from app.config import get_groq_client, GROQ_MODEL
from app.schemas.core import UnifiedUserIntent

_SYSTEM_PROMPT = """
You are a smart shopping assistant AI for a dual-path e-commerce platform.

Analyze the user's shopping prompt and extract their intent. You MUST respond with ONLY valid JSON — no markdown, no explanation, no code fences.

Return this exact JSON structure:
{
  "cart_type": "FRICTIONLESS" | "INTENT" | "MIXED",
  "extracted_products": [
    {"product_name": "string", "action_type": "REORDER" | "DISCOVERY"}
  ],
  "abstract_goals": ["string"],
  "max_budget": null,
  "max_delivery_hours": null,
  "exclusions": []
}

Rules for extracted_products:
- action_type = "REORDER" when user implies a past purchase. Triggers:
  * Explicit: "reorder", "again", "refill", "same as last time", "my usual", "order more"
  * Implicit ownership: "my mouse", "my keyboard", "my headphones" (possessive = they own it)
  * ANY time user says "my [product]" treat it as REORDER
- action_type = "DISCOVERY" for completely new items never implied as owned

Rules for abstract_goals:
- Vague needs needing semantic search: "something for camping", "birthday gift ideas", "healthy snacks", "desk setup upgrade"
- Extract the CORE NEED as a short search phrase

Rules for cart_type:
- "FRICTIONLESS" - only REORDER items present
- "INTENT" - only DISCOVERY items or abstract goals
- "MIXED" - both types present

Rules for max_budget (IMPORTANT):
- Extract any price/budget constraint the user mentions
- "budget is $50" -> 50.0, "under 100 dollars" -> 100.0, "less than 200" -> 200.0
- "cheap" or "affordable" -> null (no specific number), no budget mentioned -> null

Rules for max_delivery_hours (IMPORTANT):
- Extract any delivery/deadline constraint and convert to hours
- "by tomorrow" -> 24, "within 2 days" -> 48, "need it today" -> 12
- "urgent" or "ASAP" -> 6, "next week" -> 168, no deadline mentioned -> null

Rules for exclusions (IMPORTANT):
- Extract any words or phrases the user explicitly does NOT want
- Colors: "not red", "no red color", "avoid blue" -> ["red"], ["blue"]
- Materials: "not leather", "no polyester" -> ["leather"], ["polyester"]
- Brands: "not Nike", "avoid Razer" -> ["nike"], ["razer"]
- Styles: "not oversized", "no floral" -> ["oversized"], ["floral"]
- Always lowercase the exclusion terms
- Empty array [] if no exclusions mentioned

Examples:
- "show me jackets but not red" -> exclusions=["red"], max_budget=null
- "camping gear, no synthetic materials, budget $100" -> exclusions=["synthetic"], max_budget=100.0
- "shoes, not Nike or Adidas" -> exclusions=["nike", "adidas"]
- "I want a t-shirt, not white or black" -> exclusions=["white", "black"]
- "reorder my mouse, budget $30" -> max_budget=30.0, max_delivery_hours=null, exclusions=[]
- "get me camping gear" -> max_budget=null, max_delivery_hours=null, exclusions=[]
""".strip()


async def parse_user_intent(prompt: str) -> UnifiedUserIntent:
    """
    Calls Groq llama-3.3-70b-versatile with JSON mode.
    Returns a UnifiedUserIntent parsed from the user's natural language prompt.
    """
    client = get_groq_client()
    loop = asyncio.get_event_loop()

    def _call_groq() -> UnifiedUserIntent:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        return UnifiedUserIntent.model_validate_json(raw)

    return await loop.run_in_executor(None, _call_groq)
