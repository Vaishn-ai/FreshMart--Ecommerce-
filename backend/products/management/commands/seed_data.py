"""
Populates FreshMart with a realistic starter catalog: categories (with
subcategories), brands, and products — created one at a time with progress
output so you can see exactly what's being added.

Usage:
    python manage.py seed_data            # add everything
    python manage.py seed_data --flush    # wipe existing catalog first, then add everything
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from categories.models import Category, Brand
from products.models import Product


CATEGORIES = [
    {
        "name": "Fruits & Vegetables",
        "is_featured": True,
        "subcategories": ["Fresh Fruits", "Fresh Vegetables", "Herbs & Seasonings"],
    },
    {
        "name": "Dairy & Eggs",
        "is_featured": True,
        "subcategories": ["Milk", "Cheese & Paneer", "Curd & Yogurt", "Eggs"],
    },
    {
        "name": "Bakery",
        "is_featured": False,
        "subcategories": ["Bread", "Cakes & Pastries", "Cookies & Biscuits"],
    },
    {
        "name": "Beverages",
        "is_featured": True,
        "subcategories": ["Juices", "Soft Drinks", "Tea & Coffee", "Water"],
    },
    {
        "name": "Snacks & Namkeen",
        "is_featured": True,
        "subcategories": ["Chips & Crisps", "Namkeen", "Chocolates"],
    },
    {
        "name": "Staples & Grains",
        "is_featured": False,
        "subcategories": ["Atta & Flour", "Rice", "Pulses & Dals", "Oil & Ghee"],
    },
    {
        "name": "Personal Care",
        "is_featured": False,
        "subcategories": ["Bath & Body", "Oral Care", "Hair Care"],
    },
    {
        "name": "Household & Cleaning",
        "is_featured": False,
        "subcategories": ["Detergents", "Cleaners", "Paper Products"],
    },
    {
        "name": "Frozen Foods",
        "is_featured": False,
        "subcategories": [],
    },
    {
        "name": "Baby Care",
        "is_featured": False,
        "subcategories": [],
    },
]

BRANDS = [
    "Amul", "Mother Dairy", "Nestle", "Britannia", "Parle", "ITC",
    "Haldiram's", "Tata Consumer", "Patanjali", "Dabur", "Cadbury",
    "Coca-Cola", "PepsiCo", "Fortune", "Aashirvaad", "MTR", "Kissan",
    "Bikaji", "Surf Excel", "Colgate",
]

# Each product: (name, category, brand, unit, weight_or_size, mrp, discount_price,
#                 stock, sku, is_featured, is_flash_sale, description, highlights)
PRODUCTS = [
    # --- Fresh Fruits ---
    ("Fresh Bananas", "Fresh Fruits", None, "kg", "1kg", 60, 49, 150, "FRT-BAN-01", True, False,
     "Naturally ripened bananas, rich in potassium.", ["Rich in potassium", "Naturally ripened", "No preservatives"]),
    ("Royal Gala Apples", "Fresh Fruits", None, "kg", "1kg", 220, 189, 80, "FRT-APL-01", True, False,
     "Crisp, sweet Royal Gala apples.", ["Hand-picked", "Crisp texture", "Rich in fiber"]),
    ("Alphonso Mangoes", "Fresh Fruits", None, "kg", "1kg", 450, 399, 40, "FRT-MNG-01", True, True,
     "Premium Alphonso mangoes, the king of fruits.", ["Naturally sweet", "Seasonal specialty", "Export quality"]),
    ("Seedless Grapes", "Fresh Fruits", None, "kg", "500g", 90, 75, 100, "FRT-GRP-01", False, False,
     "Fresh green seedless grapes.", ["Seedless", "Juicy and sweet"]),
    ("Pomegranate", "Fresh Fruits", None, "kg", "1kg", 180, 159, 60, "FRT-POM-01", False, False,
     "Antioxidant-rich fresh pomegranate.", ["Rich in antioxidants", "Hand-selected"]),

    # --- Fresh Vegetables ---
    ("Organic Tomatoes", "Fresh Vegetables", None, "kg", "1kg", 50, 40, 200, "VEG-TOM-01", True, False,
     "Farm-fresh organic tomatoes.", ["100% organic", "No pesticides", "Vine-ripened"]),
    ("Onions", "Fresh Vegetables", None, "kg", "1kg", 40, 32, 300, "VEG-ONI-01", False, False,
     "Fresh red onions.", ["Long shelf life", "Farm sourced"]),
    ("Potatoes", "Fresh Vegetables", None, "kg", "1kg", 35, 28, 300, "VEG-POT-01", False, False,
     "Fresh farm potatoes.", ["Ideal for all recipes"]),
    ("Spinach (Palak)", "Fresh Vegetables", None, "pack", "250g", 25, 20, 90, "VEG-SPN-01", False, False,
     "Fresh leafy spinach, washed and packed.", ["Rich in iron", "Pre-washed"]),
    ("Bell Peppers (Capsicum)", "Fresh Vegetables", None, "kg", "500g", 80, 65, 70, "VEG-CAP-01", False, False,
     "Mixed color bell peppers.", ["Crisp and colorful", "Rich in Vitamin C"]),
    ("Cauliflower", "Fresh Vegetables", None, "pcs", "1 pc", 35, 29, 60, "VEG-CFL-01", False, False,
     "Fresh whole cauliflower.", ["Farm fresh"]),

    # --- Herbs & Seasonings ---
    ("Fresh Coriander", "Herbs & Seasonings", None, "pack", "100g", 15, 12, 120, "HRB-COR-01", False, False,
     "Freshly bunched coriander leaves.", ["Freshly cut", "Aromatic"]),
    ("Ginger", "Herbs & Seasonings", None, "g", "250g", 30, 25, 90, "HRB-GNG-01", False, False,
     "Fresh ginger root.", ["Farm fresh"]),
    ("Garlic", "Herbs & Seasonings", None, "g", "250g", 45, 38, 90, "HRB-GAR-01", False, False,
     "Fresh garlic bulbs.", ["Strong aroma", "Farm fresh"]),

    # --- Milk ---
    ("Amul Gold Full Cream Milk", "Milk", "Amul", "ml", "1L", 66, 64, 200, "DRY-MLK-01", True, False,
     "Rich and creamy full cream milk.", ["Rich in calcium", "Pasteurized", "No preservatives"]),
    ("Mother Dairy Toned Milk", "Milk", "Mother Dairy", "ml", "500ml", 27, 26, 250, "DRY-MLK-02", False, False,
     "Fresh toned milk, homogenized and pasteurized.", ["Low fat", "Pasteurized"]),

    # --- Cheese & Paneer ---
    ("Amul Fresh Paneer", "Cheese & Paneer", "Amul", "g", "200g", 90, 85, 100, "DRY-PNR-01", True, False,
     "Soft and fresh cottage cheese.", ["High in protein", "Soft texture"]),
    ("Amul Processed Cheese Slices", "Cheese & Paneer", "Amul", "pack", "10 slices", 120, 109, 80, "DRY-CHS-01", False, False,
     "Ready-to-eat cheese slices.", ["Great for sandwiches", "Rich and creamy"]),

    # --- Curd & Yogurt ---
    ("Mother Dairy Curd", "Curd & Yogurt", "Mother Dairy", "g", "400g", 40, 37, 150, "DRY-CRD-01", False, False,
     "Thick and creamy fresh curd.", ["Probiotic rich", "Set curd"]),
    ("Amul Masti Buttermilk", "Curd & Yogurt", "Amul", "ml", "200ml", 15, 14, 200, "DRY-BTM-01", False, False,
     "Spiced buttermilk, refreshing and light.", ["Refreshing", "Low fat"]),

    # --- Eggs ---
    ("Farm Fresh Eggs (12 pcs)", "Eggs", None, "pcs", "12 pcs", 84, 78, 150, "DRY-EGG-01", True, False,
     "Farm-fresh brown eggs.", ["Rich in protein", "Farm sourced"]),

    # --- Bread ---
    ("Britannia Brown Bread", "Bread", "Britannia", "pack", "400g", 45, 42, 120, "BAK-BRD-01", True, False,
     "Soft whole wheat brown bread.", ["100% whole wheat", "No maida"]),
    ("Britannia White Bread", "Bread", "Britannia", "pack", "400g", 40, 37, 120, "BAK-BRD-02", False, False,
     "Soft and fluffy white bread.", ["Soft texture", "Fresh baked"]),

    # --- Cookies & Biscuits ---
    ("Britannia Good Day Cookies", "Cookies & Biscuits", "Britannia", "g", "200g", 35, 30, 200, "BAK-CKI-01", True, False,
     "Butter cookies with cashew.", ["Rich butter taste", "Crunchy"]),
    ("Parle-G Biscuits", "Cookies & Biscuits", "Parle", "g", "200g", 20, 18, 300, "BAK-BSC-01", True, False,
     "India's favorite glucose biscuits.", ["Classic taste", "Great with tea"]),

    # --- Juices ---
    ("Tropicana Orange Juice", "Juices", "PepsiCo", "ml", "1L", 130, 115, 100, "BEV-JUI-01", True, False,
     "100% orange juice, no added sugar.", ["No added sugar", "Rich in Vitamin C"]),
    ("Real Mixed Fruit Juice", "Juices", "Dabur", "ml", "1L", 120, 105, 100, "BEV-JUI-02", False, False,
     "Blend of mixed fruit juices.", ["No preservatives"]),

    # --- Soft Drinks ---
    ("Coca-Cola", "Soft Drinks", "Coca-Cola", "ml", "750ml", 45, 42, 200, "BEV-SFT-01", False, False,
     "Classic Coca-Cola soft drink.", ["Chilled and ready to serve"]),
    ("Pepsi", "Soft Drinks", "PepsiCo", "ml", "750ml", 45, 42, 200, "BEV-SFT-02", False, False,
     "Classic Pepsi cola.", ["Refreshing taste"]),

    # --- Tea & Coffee ---
    ("Tata Tea Gold", "Tea & Coffee", "Tata Consumer", "g", "500g", 260, 235, 90, "BEV-TEA-01", True, False,
     "Rich and aromatic blended tea.", ["Rich aroma", "Long-lasting flavor"]),
    ("Nescafe Classic Coffee", "Tea & Coffee", "Nestle", "g", "100g", 280, 255, 90, "BEV-COF-01", True, False,
     "Instant coffee with rich aroma.", ["100% pure coffee", "Rich aroma"]),

    # --- Water ---
    ("Bisleri Packaged Water", "Water", None, "l", "1L", 20, 18, 300, "BEV-WTR-01", False, False,
     "Safe and pure packaged drinking water.", ["RO purified"]),

    # --- Chips & Crisps ---
    ("Lay's Classic Salted Chips", "Chips & Crisps", "PepsiCo", "g", "90g", 30, 27, 250, "SNK-CHP-01", True, False,
     "Crispy potato chips, classic salted.", ["Made from real potatoes"]),
    ("Kurkure Masala Munch", "Chips & Crisps", "PepsiCo", "g", "90g", 25, 22, 250, "SNK-CHP-02", False, False,
     "Crunchy corn snack with masala flavor.", ["Crunchy texture"]),

    # --- Namkeen ---
    ("Haldiram's Aloo Bhujia", "Namkeen", "Haldiram's", "g", "200g", 55, 49, 150, "SNK-NMK-01", True, False,
     "Crispy potato noodle snack.", ["Traditional recipe", "Crunchy"]),
    ("Bikaji Bhujia", "Namkeen", "Bikaji", "g", "200g", 50, 45, 150, "SNK-NMK-02", False, False,
     "Classic Rajasthani bhujia.", ["Authentic taste"]),

    # --- Chocolates ---
    ("Cadbury Dairy Milk", "Chocolates", "Cadbury", "g", "55g", 50, 45, 200, "SNK-CHO-01", True, False,
     "Creamy milk chocolate bar.", ["Smooth and creamy"]),
    ("Nestle KitKat", "Chocolates", "Nestle", "g", "37g", 30, 27, 200, "SNK-CHO-02", False, False,
     "Crispy wafer chocolate bar.", ["Crispy wafer layers"]),

    # --- Atta & Flour ---
    ("Aashirvaad Whole Wheat Atta", "Atta & Flour", "Aashirvaad", "kg", "5kg", 260, 235, 100, "STP-ATT-01", True, False,
     "100% whole wheat flour, stone ground.", ["100% whole wheat", "High fiber"]),

    # --- Rice ---
    ("India Gate Basmati Rice", "Rice", None, "kg", "5kg", 550, 499, 80, "STP-RIC-01", True, False,
     "Premium long-grain basmati rice.", ["Aged for aroma", "Extra-long grain"]),

    # --- Pulses & Dals ---
    ("Toor Dal (Arhar)", "Pulses & Dals", None, "kg", "1kg", 150, 135, 100, "STP-DAL-01", False, False,
     "Premium quality toor dal.", ["High in protein", "Unpolished"]),
    ("Moong Dal", "Pulses & Dals", None, "kg", "1kg", 130, 118, 100, "STP-DAL-02", False, False,
     "Split yellow moong dal.", ["Easy to digest", "High protein"]),

    # --- Oil & Ghee ---
    ("Fortune Sunflower Oil", "Oil & Ghee", "Fortune", "l", "1L", 165, 149, 120, "STP-OIL-01", True, False,
     "Refined sunflower oil, light and healthy.", ["Low in saturated fat", "Refined"]),
    ("Amul Pure Ghee", "Oil & Ghee", "Amul", "ml", "500ml", 320, 299, 90, "STP-GHE-01", True, False,
     "Pure cow ghee, rich aroma.", ["Traditional bilona method", "Rich aroma"]),

    # --- Bath & Body ---
    ("Dove Moisturizing Soap", "Bath & Body", None, "g", "100g x3", 150, 135, 100, "PC-SOP-01", False, False,
     "Moisturizing beauty bar.", ["1/4 moisturizing cream"]),

    # --- Oral Care ---
    ("Colgate Strong Teeth Toothpaste", "Oral Care", "Colgate", "g", "200g", 105, 95, 150, "PC-TPT-01", True, False,
     "Cavity protection toothpaste.", ["Anti-cavity protection"]),

    # --- Hair Care ---
    ("Dabur Amla Hair Oil", "Hair Care", "Dabur", "ml", "300ml", 175, 159, 100, "PC-HRO-01", False, False,
     "Nourishing amla hair oil.", ["Nourishes scalp", "Strengthens hair"]),

    # --- Detergents ---
    ("Surf Excel Easy Wash Detergent", "Detergents", "Surf Excel", "kg", "1kg", 130, 118, 120, "HH-DET-01", True, False,
     "Powerful stain removal detergent powder.", ["Removes tough stains", "Long-lasting freshness"]),

    # --- Cleaners ---
    ("Lizol Disinfectant Surface Cleaner", "Cleaners", None, "ml", "975ml", 210, 189, 90, "HH-CLN-01", False, False,
     "Kills 99.9% germs, floral fragrance.", ["Kills 99.9% germs"]),

    # --- Paper Products ---
    ("Origami Kitchen Tissue Roll", "Paper Products", None, "pcs", "2 rolls", 90, 79, 100, "HH-TIS-01", False, False,
     "Highly absorbent kitchen tissue.", ["Highly absorbent", "2-ply"]),

    # --- Frozen Foods (no subcategory) ---
    ("McCain French Fries", "Frozen Foods", None, "g", "425g", 150, 135, 80, "FRZ-FRY-01", True, False,
     "Crispy frozen french fries.", ["Ready in minutes", "Crispy texture"]),
    ("Amul Vanilla Ice Cream", "Frozen Foods", "Amul", "ml", "1L", 250, 225, 70, "FRZ-ICE-01", True, True,
     "Rich and creamy vanilla ice cream.", ["Made with real vanilla", "Creamy texture"]),

    # --- Baby Care (no subcategory) ---
    ("Pampers Baby Diapers", "Baby Care", None, "pcs", "36 pcs", 550, 499, 60, "BB-DIA-01", False, False,
     "Soft and absorbent baby diapers.", ["12-hour protection", "Soft on skin"]),
]


class Command(BaseCommand):
    help = "Seed FreshMart with starter categories, brands, and products (one by one, with progress output)."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing categories/brands/products first.")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing existing catalog..."))
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()

        with transaction.atomic():
            category_map = self._seed_categories()
            self._seed_brands()
            self._seed_products(category_map)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — {Category.objects.count()} categories, "
            f"{Brand.objects.count()} brands, {Product.objects.count()} products."
        ))

    def _seed_categories(self):
        self.stdout.write(self.style.MIGRATE_HEADING("\nCategories"))
        category_map = {}
        for order, entry in enumerate(CATEGORIES):
            parent, created = Category.objects.get_or_create(
                name=entry["name"],
                defaults={"is_featured": entry["is_featured"], "order": order},
            )
            self.stdout.write(f"  {'created' if created else 'exists '}  {parent.name}")
            category_map[parent.name] = parent

            for sub_order, sub_name in enumerate(entry["subcategories"]):
                sub, sub_created = Category.objects.get_or_create(
                    name=sub_name,
                    defaults={"parent": parent, "order": sub_order},
                )
                self.stdout.write(f"    {'created' if sub_created else 'exists '}  └─ {sub.name}")
                category_map[sub.name] = sub

        return category_map

    def _seed_brands(self):
        self.stdout.write(self.style.MIGRATE_HEADING("\nBrands"))
        for name in BRANDS:
            brand, created = Brand.objects.get_or_create(name=name)
            self.stdout.write(f"  {'created' if created else 'exists '}  {brand.name}")

    def _seed_products(self, category_map):
        self.stdout.write(self.style.MIGRATE_HEADING("\nProducts"))
        for (name, cat_name, brand_name, unit, size, mrp, price, stock, sku,
             featured, flash, description, highlights) in PRODUCTS:
            category = category_map.get(cat_name)
            if category is None:
                self.stdout.write(self.style.ERROR(f"  skipped  {name} (category '{cat_name}' not found)"))
                continue

            brand = Brand.objects.filter(name=brand_name).first() if brand_name else None

            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults=dict(
                    name=name, category=category, brand=brand, unit=unit,
                    weight_or_size=size, mrp=mrp, discount_price=price, stock=stock,
                    is_featured=featured, is_flash_sale=flash,
                    description=description, highlights=highlights,
                ),
            )
            self.stdout.write(f"  {'created' if created else 'exists '}  {product.name} ({sku})")
