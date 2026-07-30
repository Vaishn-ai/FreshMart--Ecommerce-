import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../services/api";
import SEO from "../components/SEO.jsx";
import { useCart } from "../contexts/CartContext.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [activeImage, setActiveImage] = useState(0);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const { addToCart } = useCart();
  const { user } = useAuth();

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get(`/products/${id}/`),
      api.get("/reviews/", { params: { product: id } }),
    ])
      .then(([p, r]) => {
        setProduct(p.data);
        setReviews(r.data.results || r.data);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-16 text-center text-gray-400">Loading...</div>;
  if (!product) return <div className="max-w-5xl mx-auto px-4 py-16 text-center">Product not found.</div>;

  const handleAddToCart = () => {
    if (!user) return toast.error("Please log in to add items to your cart");
    addToCart(product.id, 1);
  };

  const primaryImage = product.images?.[0]?.image;
  const seoDescription = product.description
    ? product.description.slice(0, 160)
    : `${product.name} — ${product.weight_or_size || product.unit}, ₹${product.discount_price} at FreshMart.`;

  const productJsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.name,
    description: seoDescription,
    image: product.images?.map((img) => img.image) || [],
    sku: product.sku,
    brand: product.brand ? { "@type": "Brand", name: product.brand.name } : undefined,
    offers: {
      "@type": "Offer",
      priceCurrency: "INR",
      price: product.discount_price,
      availability: product.in_stock
        ? "https://schema.org/InStock"
        : "https://schema.org/OutOfStock",
    },
    ...(product.rating_count > 0 && {
      aggregateRating: {
        "@type": "AggregateRating",
        ratingValue: product.rating_avg,
        reviewCount: product.rating_count,
      },
    }),
  };

  return (
    <>
      <SEO
        title={product.name}
        description={seoDescription}
        image={primaryImage}
        path={`/products/${product.id}`}
        jsonLd={productJsonLd}
      />
      <div className="max-w-5xl mx-auto px-4 py-8 grid md:grid-cols-2 gap-8">
      <div>
        <div className="aspect-square rounded-card bg-gray-50 overflow-hidden mb-3">
          {product.images?.[activeImage] ? (
            <img src={product.images[activeImage].image} alt={product.images[activeImage].alt_text || product.name} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300">No image</div>
          )}
        </div>
        <div className="flex gap-2" role="tablist" aria-label="Product images">
          {product.images?.map((img, i) => (
            <button
              key={img.id}
              role="tab"
              aria-selected={activeImage === i}
              onClick={() => setActiveImage(i)}
              className={`w-16 h-16 rounded-lg overflow-hidden border-2 ${activeImage === i ? "border-primary" : "border-transparent"}`}
            >
              <img src={img.image} alt="" className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      </div>

      <div>
        <h1 className="text-2xl font-bold mb-1">{product.name}</h1>
        <p className="text-gray-500 mb-3">{product.weight_or_size || product.unit}</p>

        <div className="flex items-baseline gap-2 mb-4">
          <span className="text-2xl font-bold">₹{product.discount_price}</span>
          {product.mrp > product.discount_price && (
            <>
              <span className="text-gray-400 line-through">₹{product.mrp}</span>
              <span className="text-accent font-semibold">{product.discount_percent}% OFF</span>
            </>
          )}
        </div>

        <button
          disabled={!product.in_stock}
          onClick={handleAddToCart}
          className="btn-primary disabled:opacity-40 mb-6"
        >
          {product.in_stock ? "Add to cart" : "Out of stock"}
        </button>

        {product.description && (
          <section className="mb-6">
            <h2 className="font-semibold mb-2">Description</h2>
            <p className="text-sm text-gray-600 dark:text-gray-300">{product.description}</p>
          </section>
        )}

        {product.highlights?.length > 0 && (
          <section className="mb-6">
            <h2 className="font-semibold mb-2">Highlights</h2>
            <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
              {product.highlights.map((h, i) => <li key={i}>{h}</li>)}
            </ul>
          </section>
        )}

        <section>
          <h2 className="font-semibold mb-2">Reviews ({reviews.length})</h2>
          {reviews.length === 0 ? (
            <p className="text-sm text-gray-400">No reviews yet.</p>
          ) : (
            <ul className="space-y-3">
              {reviews.map((r) => (
                <li key={r.id} className="border-b border-gray-100 pb-3">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <span aria-label={`${r.rating} out of 5 stars`}>{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</span>
                    <span>{r.user_name}</span>
                    {r.is_verified_purchase && <span className="text-xs text-primary">Verified Purchase</span>}
                  </div>
                  {r.title && <p className="font-medium text-sm mt-1">{r.title}</p>}
                  <p className="text-sm text-gray-600 dark:text-gray-300">{r.comment}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
      </div>
    </>
  );
}
