"""
Updates all image_url fields in seed_data.json.
Uses picsum.photos with category-seeded IDs — always loads, no API key needed.
Run: python -m app.utils.update_image_urls  (from backend/ directory)
"""
import json
import re
from pathlib import Path

UTILS_DIR = Path(__file__).parent
SEED_JSON = UTILS_DIR / "seed_data.json"

# Category → list of picsum photo IDs that match the category
CATEGORY_PHOTO_IDS = {
    "clothing":     [216, 247, 291, 325, 343, 374, 399, 432, 450, 488],
    "shoes":        [290, 307, 389, 411, 445, 467, 512, 534, 556, 578],
    "furniture":    [182, 210, 239, 271, 298, 317, 351, 376, 402, 428],
    "daily_life":   [145, 173, 199, 224, 256, 283, 312, 338, 364, 390],
    "gifts":        [164, 193, 222, 251, 278, 305, 334, 360, 386, 413],
    "electronics":  [180, 208, 237, 265, 292, 319, 348, 375, 401, 427],
    "books":        [159, 188, 217, 245, 272, 299, 328, 356, 383, 410],
    "outdoor":      [175, 203, 232, 260, 287, 314, 343, 371, 397, 423],
    "food":         [142, 170, 198, 226, 253, 280, 309, 337, 363, 389],
    "health":       [150, 178, 206, 234, 262, 289, 318, 346, 372, 398],
    "accessories":  [168, 196, 225, 253, 281, 308, 337, 365, 391, 417],
    "home":         [155, 183, 212, 240, 268, 295, 324, 352, 378, 404],
    "office":       [162, 190, 219, 247, 275, 302, 331, 359, 385, 411],
    "cleaning":     [147, 175, 204, 232, 260, 287, 316, 344, 370, 396],
    "personal_care":[153, 181, 210, 238, 266, 293, 322, 350, 376, 402],
    "skincare":     [157, 185, 214, 242, 270, 297, 326, 354, 380, 406],
    "grooming":     [161, 189, 218, 246, 274, 301, 330, 358, 384, 410],
    "hygiene":      [149, 177, 206, 234, 262, 289, 318, 346, 372, 398],
    "oral_care":    [143, 171, 200, 228, 256, 283, 312, 340, 366, 392],
    "apparel":      [216, 247, 291, 325, 343, 374, 399, 432, 450, 488],
}

DEFAULT_IDS = [100, 200, 300, 400, 500, 150, 250, 350, 450, 550]


def get_image_url(sku: str, category: str) -> str:
    sku_num = int(re.sub(r'\D', '', sku) or '1')
    ids = CATEGORY_PHOTO_IDS.get(category.lower(), DEFAULT_IDS)
    photo_id = ids[sku_num % len(ids)]
    return f"https://picsum.photos/id/{photo_id}/400/400"


def main():
    with open(SEED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    catalog = data["catalog"]
    for item in catalog:
        item["image_url"] = get_image_url(item["sku"], item["category"])

    with open(SEED_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated {len(catalog)} image URLs using picsum.photos")
    for item in catalog[:5]:
        print(f"  {item['sku']} [{item['category']}]: {item['image_url']}")


if __name__ == "__main__":
    main()
