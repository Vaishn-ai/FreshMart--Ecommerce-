"""
Project-level SEO endpoints: a live sitemap.xml built from the current product
catalog, and a robots.txt that points crawlers at it. These are intentionally
plain views rather than django.contrib.sitemaps — the project doesn't use the
sites framework anywhere else, and a hand-rolled XML response keeps this
consistent with the rest of the codebase and easy to extend (e.g. add
categories once a dedicated category-browsing page exists on the frontend).

Mounted at the project root (not /api/v1/) — see config/urls.py — so that in
production, where nginx serves the frontend and backend under one domain
(see deploy/nginx/default.conf), /sitemap.xml and /robots.txt end up on the
same origin as the pages they describe.
"""
from django.http import HttpResponse
from django.conf import settings
from products.models import Product

# (path, priority, changefreq) for pages that always exist, independent of catalog data.
# Account-specific pages (cart, checkout, orders, profile, login, etc.) are deliberately
# excluded — they're per-user and disallowed in robots.txt below.
STATIC_PAGES = [
    ("", "1.0", "daily"),
    ("/products", "0.9", "daily"),
    ("/about", "0.5", "monthly"),
    ("/contact", "0.5", "monthly"),
    ("/faq", "0.5", "monthly"),
    ("/privacy-policy", "0.3", "yearly"),
    ("/terms", "0.3", "yearly"),
]


def sitemap_view(request):
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    entries = []

    for path, priority, changefreq in STATIC_PAGES:
        entries.append(
            f"  <url>\n"
            f"    <loc>{frontend_url}{path}</loc>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    products = Product.objects.filter(is_active=True).only("id", "updated_at")
    for product in products.iterator():
        entries.append(
            f"  <url>\n"
            f"    <loc>{frontend_url}/products/{product.id}</loc>\n"
            f"    <lastmod>{product.updated_at.strftime('%Y-%m-%d')}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>0.8</priority>\n"
            f"  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")


def robots_view(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /cart",
        "Disallow: /checkout",
        "Disallow: /orders",
        "Disallow: /profile",
        "Disallow: /login",
        "Disallow: /register",
        "Disallow: /forgot-password",
        "Disallow: /admin/",
        "Disallow: /api/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
