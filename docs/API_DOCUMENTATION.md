# FreshMart — API Documentation

Base URL: `http://localhost:8000/api/v1/` (local) or `https://<your-render-app>.onrender.com/api/v1/` (production).
Interactive Swagger UI is auto-generated at **`/api/docs/`**.

Auth: JWT via `Authorization: Bearer <access_token>` header. Access tokens last 30 minutes; refresh tokens last 7 days and rotate on use.

---

## Auth (`/auth/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register/` | – | Register; returns `access`/`refresh` tokens |
| POST | `/auth/login/` | – | Login with `email`+`password`; returns tokens + user |
| POST | `/auth/token/refresh/` | – | Exchange `refresh` for a new `access` |
| POST | `/auth/logout/` | ✓ | Blacklists the refresh token |
| GET/PATCH | `/auth/profile/` | ✓ | View/update own profile |
| POST | `/auth/change-password/` | ✓ | `old_password`, `new_password` |
| POST | `/auth/forgot-password/` | – | Sends reset email |
| POST | `/auth/reset-password/` | – | `uid`, `token`, `new_password` |
| GET/POST | `/auth/addresses/` | ✓ | List / create addresses |
| GET/PATCH/DELETE | `/auth/addresses/{id}/` | ✓ | Manage one address |

## Categories & Brands (`/categories/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/categories/` | – | Top-level categories with nested subcategories |
| GET | `/categories/{id}/` | – | One category |
| POST/PATCH/DELETE | `/categories/{id}/` | admin | Manage categories |
| GET | `/categories/brands/` | – | List brands |

## Products (`/products/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/products/` | – | List, paginated. Query params: `search`, `ordering`, `category`, `brand`, `min_price`, `max_price`, `min_rating`, `in_stock`, `is_featured`, `is_flash_sale` |
| GET | `/products/{id}/` | – | Full detail (images, variants, specs) |
| POST | `/products/` | admin | Create |
| PATCH/DELETE | `/products/{id}/` | admin | Update / delete |
| GET | `/products/featured/` | – | Featured products (cached 60s) |
| GET | `/products/flash-sale/` | – | Active flash-sale products |
| GET | `/products/best-sellers/` | – | Sorted by `sold_count` |
| GET | `/products/trending/` | – | Rating + activity proxy |
| GET | `/products/recommended/` | – | Personalized if authenticated, else top-rated |
| GET | `/products/recently-viewed/` | ✓ | Last 20 viewed products |
| GET | `/products/autocomplete/?q=` | – | Name suggestions (min 2 chars) |
| GET | `/products/compare/?ids=a,b,c` | – | Full detail for up to 4 products |
| GET | `/products/search/recent/` | ✓ | Own last 10 distinct searches |
| DELETE | `/products/search/recent/` | ✓ | Clear own search history |
| GET | `/products/search/trending/` | – | Top queries in last 7 days |
| POST | `/products/search/voice/` | – | `{transcript}` → matched products |

## Cart (`/cart/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/cart/` | ✓ | Current cart (items, saved-for-later, totals) |
| POST | `/cart/add/` | ✓ | `{product_id, variant_id?, quantity}` |
| PATCH | `/cart/items/{item_id}/` | ✓ | `{quantity}` |
| DELETE | `/cart/items/{item_id}/` | ✓ | Remove item |
| POST | `/cart/items/{item_id}/save-for-later/` | ✓ | Move to saved-for-later |
| DELETE | `/cart/items/{item_id}/save-for-later/` | ✓ | Move back to active cart |
| DELETE | `/cart/clear/` | ✓ | Empty active cart |
| POST | `/cart/coupon/` | ✓ | `{code}` — apply |
| DELETE | `/cart/coupon/` | ✓ | Remove applied coupon |

## Wishlist (`/wishlist/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/wishlist/` | ✓ | List |
| POST | `/wishlist/` | ✓ | `{product_id}` — add |
| DELETE | `/wishlist/{product_id}/` | ✓ | Remove |
| POST | `/wishlist/{product_id}/move-to-cart/` | ✓ | Move to cart, removes from wishlist |

## Coupons (`/coupons/`) — admin management
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET/POST | `/coupons/` | admin | List / create |
| GET/PATCH/DELETE | `/coupons/{id}/` | admin | Manage one |

## Orders (`/orders/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/orders/checkout/` | ✓ | `{address_id, shipping_method, payment_method}` → creates Order from cart |
| GET | `/orders/` | ✓ | Own orders (all orders if staff) |
| GET | `/orders/{id}/` | ✓ | Order detail with items + status timeline |
| POST | `/orders/{id}/cancel/` | ✓ | Cancel (only if not shipped/delivered) |
| GET | `/orders/{id}/invoice/` | ✓ | Download PDF invoice |
| GET | `/orders/{id}/track/` | ✓ | Status + timeline |
| POST | `/orders/{id}/status/` | admin | `{status, note?, tracking_number?}` — advance order |

## Payments (`/payments/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/payments/razorpay/create/{order_id}/` | ✓ | Creates a Razorpay order, returns `razorpay_order_id` for Checkout.js |
| POST | `/payments/razorpay/verify/` | ✓ | `{order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature}` |
| POST | `/payments/stripe/create-intent/{order_id}/` | ✓ | Returns `client_secret` for Stripe Elements |
| POST | `/payments/stripe/confirm/` | ✓ | `{order_id, payment_intent_id}` |
| POST | `/payments/upi/initiate/` | ✓ | `{order_id, upi_id}` → UPI deep link |

## Reviews & Q&A (`/reviews/`, `/questions/`)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/reviews/?product={id}` | – | Reviews for a product |
| POST | `/reviews/` | ✓ | `{product, rating, title?, comment?}` |
| PATCH/DELETE | `/reviews/{id}/` | ✓ (owner) | Edit/delete own review |
| POST | `/reviews/{id}/helpful/` | ✓ | Vote helpful (once per user) |
| GET | `/questions/?product={id}` | – | Q&A for a product |
| POST | `/questions/` | ✓ | `{product, question}` |
| POST | `/questions/{id}/answer/` | ✓ | `{answer}` — seller answers flagged automatically if staff |
| GET | `/products/{id}/frequently-bought-together/` | – | Up to 6 co-purchased products |

## Admin Dashboard (`/dashboard/`) — all admin-only
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary/` | Headline KPIs for the dashboard home screen |
| GET | `/dashboard/analytics/revenue/?days=30` | Daily revenue + order counts |
| GET | `/dashboard/analytics/sales/` | Status/payment breakdown + best sellers |
| GET | `/dashboard/analytics/customers/` | Customer counts + top spenders |
| GET | `/dashboard/inventory/` | Full stock listing |
| GET | `/dashboard/inventory/low-stock/?threshold=10` | Low-stock alerts |
| GET | `/dashboard/export/orders.csv` | CSV export |
| GET | `/dashboard/export/products.csv` | CSV export |

---

## Pagination
All list endpoints use `PageNumberPagination`, page size 12: `?page=2`. Response shape:
```json
{ "count": 42, "next": "...", "previous": null, "results": [...] }
```

## Error format
```json
{ "detail": "Human-readable message." }
```
or, for field validation, DRF's standard `{ "field_name": ["error"] }`.

## Rate limits
Anonymous: 100 req/hour. Authenticated: 1000 req/hour (configurable in `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES`).
