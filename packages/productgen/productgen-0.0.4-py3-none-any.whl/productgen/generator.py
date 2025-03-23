import random
import os
import json
from enum import Enum

class Style(Enum):
    SIMPLE_CONCAT = 1
    HYPHENATION = 2
    TITLE_CASE = 3
    CAPITALIZATION = 4
    RANDOM_CAPITALIZATION = 5
    RANDOM_WORD_ORDER = 6

def load_data_from_json(filename):
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "data", filename)
    if not os.path.exists(data_path):
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

PRODUCT_BRANDS = load_data_from_json("product_brands.json").get("brands", [])
# Ubah sesuai kebutuhan, misalnya product_categories.json, dsb.

def generate_product_name(style, brand=None, use_suffix=False, use_tagline=False):
    if brand is None:
        brand = random.choice(PRODUCT_BRANDS) if PRODUCT_BRANDS else "DefaultBrand"

    category = "ExampleCat"
    subcategory = "CatSub"

    if style == Style.SIMPLE_CONCAT:
        product_name = f"{category} {subcategory}"
    elif style == Style.HYPHENATION:
        product_name = f"{category}-{subcategory}"
    elif style == Style.TITLE_CASE:
        product_name = f"{category.title()} {subcategory.title()}"
    elif style == Style.CAPITALIZATION:
        product_name = f"{category.capitalize()} {subcategory.capitalize()}"
    elif style == Style.RANDOM_CAPITALIZATION:
        product_name = f"{random.choice([category.upper(), category.lower()])} {random.choice([subcategory.upper(), subcategory.lower()])}"
    elif style == Style.RANDOM_WORD_ORDER:
        product_name = f"{subcategory} {category}"
    else:
        raise ValueError("Invalid style")

    if use_suffix:
        product_name += f" {random.randint(100, 999)}"

    if use_tagline:
        product_name += " AwesomeTag"

    return f"{brand} {product_name}"