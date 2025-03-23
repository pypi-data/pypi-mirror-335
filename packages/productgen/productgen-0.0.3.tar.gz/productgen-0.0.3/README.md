# product generator

## What can do?
- Make a product name automatically

# How To Usage ?

```py
# file: example_usage.py
from product_generator.generator import generate_product_name, Style

if __name__ == "__main__":
    # Menghasilkan nama produk sederhana
    result = generate_product_name(Style.SIMPLE_CONCAT)
    print("Contoh nama produk:", result)

    # Menghasilkan nama produk dengan brand, suffix, dan tagline
    fancy_name = generate_product_name(
        Style.TITLE_CASE,
        brand="ContohBrand",
        use_suffix=True,
        use_tagline=True
    )
    print("Contoh nama produk yang lebih lengkap:", fancy_name)
```
