# FreshMart — Testing Guide

## Backend (Django)

### Run the suite
```bash
cd backend
python manage.py test                                  # all apps
python manage.py test accounts products cart orders    # specific apps
python manage.py test cart.tests.CartTests.test_apply_valid_coupon  # one test
```
Tests use Django's `TestCase` / DRF's `APITestCase`, which wrap each test in a transaction and roll it back — no separate test-DB setup needed beyond what `DATABASES` in `.env` points at (Django auto-creates/drops `test_<DB_NAME>`).

### What's covered today
| App | File | Covers |
|---|---|---|
| accounts | `accounts/tests.py` | Register (success + password mismatch), login (valid/invalid), profile auth-gating, address CRUD, single-default-address invariant |
| products | `products/tests.py` | Listing, category filter, in-stock filter, featured endpoint, search, discount % calculation, detail retrieve, admin-only write permission |
| cart | `cart/tests.py` | Add/update/remove items, stock-limit rejection, totals math, save-for-later, coupon apply (valid + expired), auth requirement |
| orders | `orders/tests.py` | Checkout service (order creation, stock decrement, empty-cart error, online-payment leaves order pending, express surcharge), checkout endpoint, order list scoping (users only see their own), cancel flow (allowed pre-shipping, blocked post-delivery) |

### Gaps to close next (not blocking, but worth adding before a real launch)
- `wishlist`, `coupons` (admin CRUD), `payments` (mock the Razorpay/Stripe SDK calls), `reviews`/Q&A, `dashboard` analytics
- Model-level tests for `Product.discount_percent`/`in_stock`, `Cart.total` edge cases (free-delivery threshold, zero-subtotal)
- Permission tests for every admin-only endpoint (`IsAdminUser` denial for regular users)

### Manual smoke test checklist (run once per deploy)
1. Register → receive tokens → GET `/auth/profile/` succeeds
2. Login with wrong password → 401
3. Browse `/products/`, filter by category/price, search a known product name
4. Add to cart, change quantity past stock → 400, apply a coupon, remove it
5. Checkout with COD → order appears in `/orders/`, stock decremented
6. Cancel that order → status flips to `cancelled`
7. Leave a review on a delivered order → `rating_avg` on the product updates
8. Hit `/dashboard/summary/` as staff → 200; as a normal user → 403
9. Download an invoice PDF and confirm it opens

## Frontend (React)
No test runner is wired up yet (Vitest/RTL would be the natural choice — deliberately left out of Phases 1-9 to keep scope on delivering working features first). In the meantime:

### Manual verification checklist
- [ ] Every route in `App.jsx` loads without a blank screen or console error: `/`, `/products`, `/products/:id`, `/cart`, `/wishlist`, `/checkout`, `/orders`, `/profile`, `/login`, `/register`, `/forgot-password`, `/about`, `/contact`, `/faq`, `/privacy-policy`, `/terms`, and an unknown path (→ 404 page)
- [ ] Network tab: confirm JWT `Authorization` header is attached once logged in, and that a 401 triggers the refresh-token flow (`services/api.js` interceptor)
- [ ] Cart badge count updates immediately after Add to Cart
- [ ] Resize to 375px width — layout should never horizontally scroll; nav collapses to the hamburger menu
- [ ] Tab through the header (skip link → menu button → search → wishlist → cart → login/profile) — focus order should be logical and visible
- [ ] Toggle a screen reader (or browser accessibility inspector) on the Cart and Checkout pages — form inputs should announce their labels

### Adding real automated frontend tests (recommended next step)
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```
Then add a `vitest.config.js` extending the Vite config with `test: { environment: 'jsdom' }`, and start with `ProductCard.test.jsx` (renders name/price, calls `onAddToCart`) and `CartContext.test.jsx` (mocking `api.js` with `vi.mock`).

## API testing via Postman
Import `docs/postman_collection.json` — organized by app (Auth, Products, Cart, Orders, Payments, Reviews, Dashboard) with a collection-level `{{base_url}}` variable and a post-login test script that auto-saves `{{access_token}}`/`{{refresh_token}}` into collection variables so every subsequent request authenticates automatically.

## CI
Every push runs the backend test suite against real Postgres + Redis service containers, plus a frontend build — see `.github/workflows/ci.yml`. A red CI run should block merging; there's no automated deploy gate beyond that in this setup.
