import { Helmet } from "react-helmet-async";

const SITE_NAME = "FreshMart";
const DEFAULT_DESCRIPTION = "Fresh groceries, delivered fast. Shop fruits, vegetables, dairy, snacks, and everyday essentials at everyday low prices.";
const DEFAULT_IMAGE = "/og-image.png";
const SITE_URL = import.meta.env.VITE_SITE_URL || "https://freshmart-ecommerce-pied.vercel.app";

/**
 * Drop into any page to set its title, meta description, canonical URL,
 * Open Graph / Twitter Card tags, and (optionally) JSON-LD structured data.
 *
 * <SEO title="Fresh Bananas" description="..." image={product.primary_image}
 *      path={`/products/${id}`} jsonLd={productJsonLd} />
 *
 * `noindex` is for pages that should never appear in search results —
 * cart, checkout, orders, profile, auth pages, etc.
 */
export default function SEO({
  title,
  description = DEFAULT_DESCRIPTION,
  image = DEFAULT_IMAGE,
  path = "",
  noindex = false,
  jsonLd = null,
}) {
  const fullTitle = title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} — Fresh groceries, delivered fast`;
  const canonical = `${SITE_URL}${path}`;
  const absoluteImage = image?.startsWith("http") ? image : `${SITE_URL}${image}`;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={canonical} />
      {noindex && <meta name="robots" content="noindex, nofollow" />}

      {/* Open Graph */}
      <meta property="og:type" content={path.startsWith("/products/") ? "product" : "website"} />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={absoluteImage} />
      <meta property="og:url" content={canonical} />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={absoluteImage} />

      {jsonLd && <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>}
    </Helmet>
  );
}
