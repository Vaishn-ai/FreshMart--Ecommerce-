# FreshMart — Adding Catalog Data via Django Admin

A field-by-field walkthrough for adding categories, brands, and products yourself through the admin panel, plus a reference checklist of realistic starter data if you want something to copy from while you go.

## 1. Get into the admin

```bash
cd backend
python manage.py createsuperuser   # if you haven't already
python manage.py runserver
```
Open **http://localhost:8000/admin/** and log in.

Do things in this order — **Categories → Brands → Products** — since a Product requires a Category and can optionally reference a Brand.

---

## 2. Adding a Category

Go to **Categories → Add Category**. Fields you'll see, in order:

| Field | What to enter |
|---|---|
| Name | e.g. `Fruits & Vegetables` |
| Slug | Leave blank — it auto-fills from Name as you type (watch it populate live) |
| Parent | Leave empty for a top-level category. To add a **subcategory**, pick the top-level one here (e.g. parent = `Fruits & Vegetables`, name = `Fresh Fruits`) |
| Image | Optional — upload a category banner/icon |
| Is featured | Check this to show it in "featured categories" sections |
| Is active | Leave checked |
| Order | Lower numbers show first (0, 1, 2...) |

Click **Save**. To add a subcategory, repeat and set **Parent** to the category you just created.

---

## 3. Adding a Brand

Go to **Brands → Add Brand**:

| Field | What to enter |
|---|---|
| Name | e.g. `Amul` |
| Slug | Auto-fills from Name |
| Logo | Optional image upload |
| Is active | Leave checked |

---

## 4. Adding a Product

Go to **Products → Add Product**. This form has more fields — here's what each one means:

| Field | Notes |
|---|---|
| Name | Product name, e.g. `Fresh Bananas` |
| Slug | Auto-fills from Name |
| Category | Pick from the dropdown (must exist already) |
| Brand | Optional — leave blank for unbranded produce |
| Description | Free text |
| Highlights | **JSON list** — type exactly like this: `["Rich in potassium", "Naturally ripened", "No preservatives"]` |
| Specifications | **JSON object** — e.g. `{"Origin": "India", "Shelf Life": "5 days"}` |
| Nutrition facts | **JSON object** — e.g. `{"Calories": "89 kcal", "Protein": "1.1g"}` |
| Unit | Dropdown: Kg / Gram / Litre / ml / Pieces / Pack |
| Weight or size | Free text, e.g. `1kg`, `500ml`, `12 pcs` |
| Color | Optional, mostly for non-food items |
| MRP | Original price |
| Discount price | Selling price — must be ≤ MRP |
| Stock | Quantity available |
| SKU | **Must be unique** — pick a short code, e.g. `FRT-BAN-01` |
| Barcode | Optional |
| Is featured | Shows on the homepage "Featured" section |
| Is flash sale | Shows in flash-sale listings |
| Flash sale ends at | Only needed if "Is flash sale" is checked |
| Is active | Leave checked to make it visible in the shop |

**Below the main form**, two inline sections let you add images and variants without leaving the page:
- **Product images** — upload one or more images, check "Is primary" on the one that should show in listings
- **Product variants** — for size/weight/color options (e.g. "500g" vs "1kg"), each with its own SKU, price, and stock

Click **Save**.

> **Tip on the JSON fields:** if you leave Highlights/Specifications/Nutrition facts blank, Django will save them as an empty list/dict — that's fine, they're optional. Just make sure whatever you type is valid JSON (double quotes, not single quotes) or the form will show a validation error.

---

## 5. Reference checklist (optional — copy from this as you go)

### Categories to create (create the bold ones first, then their subcategories)
- **Fruits & Vegetables** → Fresh Fruits, Fresh Vegetables, Herbs & Seasonings
- **Dairy & Eggs** → Milk, Cheese & Paneer, Curd & Yogurt, Eggs
- **Bakery** → Bread, Cakes & Pastries, Cookies & Biscuits
- **Beverages** → Juices, Soft Drinks, Tea & Coffee, Water
- **Snacks & Namkeen** → Chips & Crisps, Namkeen, Chocolates
- **Staples & Grains** → Atta & Flour, Rice, Pulses & Dals, Oil & Ghee
- **Personal Care** → Bath & Body, Oral Care, Hair Care
- **Household & Cleaning** → Detergents, Cleaners, Paper Products
- **Frozen Foods** (no subcategories)
- **Baby Care** (no subcategories)

### Brands to create
Amul · Mother Dairy · Nestle · Britannia · Parle · ITC · Haldiram's · Tata Consumer · Patanjali · Dabur · Cadbury · Coca-Cola · PepsiCo · Fortune · Aashirvaad · MTR · Kissan · Bikaji · Surf Excel · Colgate

### A few products per category to start with
| Category | Product | Brand | Size | MRP → Price | SKU |
|---|---|---|---|---|---|
| Fresh Fruits | Fresh Bananas | — | 1kg | 60 → 49 | FRT-BAN-01 |
| Fresh Fruits | Royal Gala Apples | — | 1kg | 220 → 189 | FRT-APL-01 |
| Fresh Vegetables | Organic Tomatoes | — | 1kg | 50 → 40 | VEG-TOM-01 |
| Milk | Amul Gold Full Cream Milk | Amul | 1L | 66 → 64 | DRY-MLK-01 |
| Cheese & Paneer | Amul Fresh Paneer | Amul | 200g | 90 → 85 | DRY-PNR-01 |
| Bread | Britannia Brown Bread | Britannia | 400g | 45 → 42 | BAK-BRD-01 |
| Juices | Tropicana Orange Juice | PepsiCo | 1L | 130 → 115 | BEV-JUI-01 |
| Chips & Crisps | Lay's Classic Salted Chips | PepsiCo | 90g | 30 → 27 | SNK-CHP-01 |
| Atta & Flour | Aashirvaad Whole Wheat Atta | Aashirvaad | 5kg | 260 → 235 | STP-ATT-01 |
| Oral Care | Colgate Strong Teeth Toothpaste | Colgate | 200g | 105 → 95 | PC-TPT-01 |
| Detergents | Surf Excel Easy Wash Detergent | Surf Excel | 1kg | 130 → 118 | HH-DET-01 |
| Frozen Foods | Amul Vanilla Ice Cream | Amul | 1L | 250 → 225 | FRZ-ICE-01 |

Add a couple per category and your storefront will already look populated — you can always add more later.

---

## 6. If you'd rather not type everything by hand later
There's also an automated command (`python manage.py seed_data`) covering the full 10-category / 20-brand / 53-product starter catalog in one go, if you ever want to bulk-fill the rest after getting comfortable with the admin forms above. Entirely optional — this guide is for doing it manually.
