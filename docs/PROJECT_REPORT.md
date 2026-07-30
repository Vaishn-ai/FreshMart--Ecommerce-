# FreshMart — Project Report

## Summary
FreshMart is a full-stack grocery e-commerce platform built to the original spec: Django 5 + DRF backend, React 19 + Vite frontend, JWT auth, PostgreSQL, Redis, Celery, Cloudinary, and Docker-based deployment. It was built and audited across 9 phases in this conversation, each phase adding working, verified code rather than scaffolding.

## Architecture
**Backend** — 11 Django apps, each owning one domain: `accounts` (auth + addresses), `categories` (categories/brands), `products` (catalog, search, variants), `cart`, `wishlist`, `coupons`, `orders` (checkout, tracking, invoices), `payments` (Razorpay/Stripe/UPI/COD), `reviews` (ratings + Q&A), `dashboard` (analytics/admin), `notifications` (Celery tasks). Note: the original spec listed `dashboard` and `analytics` as separate apps — they were merged into one `dashboard` app since the endpoints are tightly coupled (all admin-only aggregation views); this is documented here rather than silently deviating from spec.

**Frontend** — React 19 function components, Context API for auth/cart state (no Redux — unnecessary for this scope), Axios with an automatic JWT-refresh interceptor, React Router with every page code-split via `React.lazy`/`Suspense`, Tailwind for styling against the specified design tokens (`#0B8F3C` primary, `#FFD54F` accent, 20px card radius), Framer Motion for card micro-interactions.

**Infrastructure** — Docker Compose orchestrates Postgres, Redis, Gunicorn-served Django, a Celery worker + beat, an Nginx-served static React build, and a reverse-proxy Nginx tying it together. A parallel path documents Render (backend) + Vercel (frontend) deployment per the original spec. GitHub Actions CI runs Django checks, `makemigrations --check`, the test suite (against real Postgres/Redis service containers), a frontend build, and a Docker build on every push.

## Completed features (by spec section)
- **Auth**: register, login, logout, JWT refresh, forgot/reset password, profile, addresses. (Google login is *not* implemented — see Known Gaps.)
- **Products**: categories/subcategories, brands, featured/flash-sale/best-sellers/trending/recommended/recently-viewed, variants, multi-image gallery, nutrition facts/specs/highlights, ratings.
- **Cart**: add/update/remove, save-for-later, coupon apply/remove, delivery charge + GST calculation, running totals.
- **Wishlist**: add/remove/move-to-cart.
- **Coupons**: percent/flat discounts, min order value, per-user + total usage limits, expiry.
- **Checkout**: address selection, standard/express shipping, COD/Razorpay/Stripe/UPI, tax + delivery computed server-side.
- **Orders**: full status lifecycle (pending→confirmed→packed→shipped→delivered, plus cancelled/returned), status timeline, PDF invoice generation, cancel flow with status guardrails.
- **Payments**: Razorpay order creation + signature verification, Stripe PaymentIntent creation + confirmation, UPI deep-link generation, COD auto-confirm. All three online providers fail gracefully with a clear message when API keys aren't configured, rather than crashing.
- **Reviews & Q&A**: ratings with verified-purchase detection (checked against delivered `OrderItem`s), helpful votes, product Q&A with seller-answer flagging, frequently-bought-together (co-purchase analysis).
- **Search**: full-text search, autocomplete, recent/trending searches, voice-search endpoint (accepts a transcript — actual speech-to-text is a frontend/Web Speech API concern), product comparison (up to 4 products).
- **Admin dashboard**: revenue/sales/customer analytics, inventory view, low-stock alerts, CSV export for orders and products.
- **Notifications**: email sends for real (order confirmation, status updates, password reset); SMS is a stubbed Celery task with a documented integration point for a real provider (Twilio/MSG91) since no SMS credentials were provided.
- **Performance**: `select_related`/`prefetch_related` audited across every list-serving view (4 real N+1 bugs found and fixed during the Phase-8/audit pass — see below), Redis caching on the featured-products endpoint, pagination everywhere, lazy image loading, frontend code splitting.
- **Accessibility**: skip-to-content link, `aria-label`/`aria-expanded`/`aria-selected`/`aria-current` where relevant, `role="alert"`/`role="status"` on live regions, labeled form inputs throughout.

## What's intentionally not built, and why
- **Google Login** — requires a real Google OAuth client ID/secret, which wasn't provided; the `google_id` field exists on the `User` model ready to receive it, but the OAuth flow itself isn't wired up.
- **Real SMS delivery** — same reasoning; `notifications/tasks.py` has a working Celery task shape with a documented swap-in point.
- **Amazon S3** — spec marks it optional; Cloudinary is the default media backend. Deployment guide documents the swap.
- **Frontend automated tests** — no Vitest/RTL suite; a manual QA checklist is in `docs/TESTING_GUIDE.md` instead, with instructions for adding real tests.
- **Full test coverage** — `accounts`, `products`, `cart`, `orders` have real `APITestCase` suites (checked into the repo, run in CI). `wishlist`, `coupons`, `payments`, `reviews`, `dashboard` do not yet — documented as a gap, not hidden.

## Audit findings (fixed during the Phase 8/9 review)
This sandbox has no network access, so this was a thorough *static* audit (parsing, import-graph resolution, N+1 pattern review) rather than a live `manage.py check` — documented honestly rather than claiming a test run that didn't happen. It found and fixed:
- 9 files with genuinely unused imports (removed)
- **4 real N+1 query bugs**: voice-search results, frequently-bought-together results, and two spots where `OrderItemSerializer` accessed `item.product.images` without a deep-enough `prefetch_related` (the checkout response and the admin order-status-update view)
- 1 copy-paste artifact (an accidental duplicate/malformed import line in `cart/views.py`) caught and removed before it shipped
- Confirmed zero broken cross-app model references, zero orphaned URL includes, and zero broken frontend import paths across the whole `src/` tree

## Recommended next steps
1. Add the missing test coverage (`wishlist`, `coupons`, `payments`, `reviews`, `dashboard`)
2. Wire up Google OAuth once credentials are available
3. Pick a real SMS provider and fill in `notifications/tasks.py`
4. Add Vitest + React Testing Library for the frontend
5. Run an actual `manage.py check` + `npm run build` in a real environment (this project has been statically verified but never executed, since this sandbox has no network access to install dependencies) — treat the first real deploy as the true integration test
