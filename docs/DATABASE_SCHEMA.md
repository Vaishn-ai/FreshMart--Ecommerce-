# FreshMart — Database Schema

PostgreSQL. All primary keys are UUIDs (except Django's internal auth/admin tables). This mirrors `models.py` in each app — treat the code as source of truth if they ever drift.

## accounts
**User** (extends `AbstractUser`, `AUTH_USER_MODEL`)
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| email | varchar, unique | login identifier (`USERNAME_FIELD`) |
| username | varchar | required, not unique |
| phone | varchar | |
| profile_image | image | |
| is_email_verified | bool | |
| google_id | varchar, unique, nullable | Google OAuth |
| created_at / updated_at | datetime | |

**Address**
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | FK → User | |
| label | enum(home/work/other) | |
| full_name, phone, line1, line2, city, state, pincode, country | varchar | |
| is_default | bool | only one per user (enforced in `save()`) |

## categories
**Category**: id, name (unique), slug (unique), parent_id (FK self, nullable), image, is_featured, is_active, order
**Brand**: id, name (unique), slug (unique), logo, is_active

## products
**Product**
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name, slug (unique) | varchar | |
| category_id | FK → Category (PROTECT) | |
| brand_id | FK → Brand (SET_NULL), nullable | |
| description | text | |
| highlights | JSON list | |
| specifications | JSON dict | |
| nutrition_facts | JSON dict | |
| unit | enum(kg/g/l/ml/pcs/pack) | |
| weight_or_size, color | varchar | |
| mrp, discount_price | decimal(10,2) | |
| stock | int | |
| sku | varchar, unique | |
| barcode | varchar | |
| is_featured, is_flash_sale, is_active | bool | |
| flash_sale_ends_at | datetime, nullable | |
| rating_avg | decimal(3,2) | denormalized, recalculated on review CRUD |
| rating_count, sold_count | int | denormalized |

**ProductImage**: id, product_id (FK), image, alt_text, is_primary, order
**ProductVariant**: id, product_id (FK), name, sku (unique), mrp, discount_price, stock, is_active
**RecentlyViewed**: id, user_id (FK), product_id (FK), viewed_at — unique(user, product)
**SearchLog**: id, user_id (FK, nullable), query, result_count, created_at

## cart
**Cart**: id, user_id (FK, OneToOne), coupon_id (FK, nullable) — totals (`subtotal`, `discount_amount`, `delivery_charge`, `tax_amount`, `total`) are computed properties, not stored columns
**CartItem**: id, cart_id (FK), product_id (FK), variant_id (FK, nullable), quantity, saved_for_later — unique(cart, product, variant)

## coupons
**Coupon**: id, code (unique), discount_type (percent/flat), discount_value, max_discount_amount, min_order_value, usage_limit_total, usage_limit_per_user, times_used, valid_from, valid_until, is_active
**CouponUsage**: id, coupon_id (FK), user_id (FK), order_id (UUID, nullable), used_at — unique(coupon, user, order_id)

## orders
**Order**
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| order_number | varchar, unique | auto-generated `FM<timestamp><random>` |
| user_id | FK → User (PROTECT) | |
| shipping_* | varchar | **snapshot** of the Address at order time |
| shipping_method | enum(standard/express) | |
| subtotal, discount_amount, delivery_charge, tax_amount, total | decimal(10,2) | |
| coupon_id | FK, nullable | |
| payment_method | enum(cod/stripe/razorpay/upi) | |
| payment_status | enum(pending/paid/failed/refunded) | |
| status | enum(pending/confirmed/packed/shipped/delivered/cancelled/returned) | |
| tracking_number | varchar | |

**OrderItem**: id, order_id (FK), product_id (FK, PROTECT), variant_id (FK, nullable), product_name, unit_price, quantity — all **snapshotted** at purchase time
**OrderStatusHistory**: id, order_id (FK), status, note, changed_at — append-only timeline

## payments
**Payment**: id, order_id (FK, OneToOne), provider, provider_order_id, provider_payment_id, provider_signature, amount, currency, status, raw_response (JSON)

## reviews
**Review**: id, product_id (FK), user_id (FK), rating (1-5), title, comment, is_verified_purchase, helpful_count — unique(product, user)
**ReviewImage**: id, review_id (FK), image
**ReviewHelpfulVote**: id, review_id (FK), user_id (FK) — unique(review, user)
**ProductQuestion**: id, product_id (FK), user_id (FK), question
**ProductAnswer**: id, question_id (FK), user_id (FK), answer, is_seller_answer, helpful_count

## Indexes worth knowing about
- `Product`: indexed on `is_featured`, `is_flash_sale`, `-sold_count`
- `Order`: indexed on `status`, `(user, -created_at)`
- All FK columns get an implicit index from Django/Postgres

## Generating the real migration files
This repo ships model definitions but not pre-baked migration files (they're environment/Postgres-version specific). Generate them locally:
```bash
cd backend
python manage.py makemigrations accounts categories products cart wishlist coupons orders payments reviews
python manage.py migrate
```
