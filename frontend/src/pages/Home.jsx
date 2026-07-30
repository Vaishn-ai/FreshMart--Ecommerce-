import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import ProductCard from "../components/ProductCard.jsx";
import SEO from "../components/SEO.jsx";
import { useCart } from "../contexts/CartContext.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";

const homeJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "FreshMart",
  description:
    "Fresh groceries, delivered fast. Shop fruits, vegetables, dairy, snacks, and everyday essentials at everyday low prices.",
};

export default function Home() {
  const [featured, setFeatured] = useState([]);
  const [loading, setLoading] = useState(true);

  const { addToCart } = useCart();
  const { user } = useAuth();

  const loadFeatured = async () => {
    try {
      setLoading(true);

      const { data } = await api.get("/products/featured/");

      setFeatured(data.results || data);
    } catch (err) {
      console.error(err);
      toast.error("Unable to load products");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeatured();
  }, []);

  const handleAddToCart = (product) => {
    if (!user) {
      toast.error("Please log in to add items to your cart");
      return;
    }

    addToCart(product.id, 1);
  };

  const handleToggleWishlist = async (product) => {
    if (!user) {
      toast.error("Please log in to use your wishlist");
      return;
    }

    try {
      if (product.is_wishlisted) {
        await api.delete(`/wishlist/${product.id}/`);

        setFeatured((prev) =>
          prev.map((p) =>
            p.id === product.id
              ? { ...p, is_wishlisted: false }
              : p
          )
        );

        toast.success("Removed from wishlist 💔");
      } else {
        await api.post("/wishlist/", {
          product_id: product.id,
        });

        setFeatured((prev) =>
          prev.map((p) =>
            p.id === product.id
              ? { ...p, is_wishlisted: true }
              : p
          )
        );

        toast.success("Added to wishlist ❤️");
      }
    } catch (err) {
      console.error(err);
      toast.error("Could not update wishlist");
    }
  };

  return (
    <>
      <SEO path="/" jsonLd={homeJsonLd} />

      <main className="min-h-screen bg-bg dark:bg-gray-950 px-4 py-6">
        <section className="rounded-card bg-gradient-to-br from-primary to-emerald-600 text-white p-8 mb-8">
          <h1 className="text-2xl font-bold mb-2">
            Fresh groceries, delivered fast 🥬
          </h1>

          <p className="text-white/80">
            Everyday essentials at everyday low prices.
          </p>
        </section>

        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Featured products
        </h2>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div
                key={i}
                className="card h-64 animate-pulse bg-gray-100 dark:bg-gray-800"
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {featured.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                onToggleWishlist={handleToggleWishlist}
              />
            ))}
          </div>
        )}
      </main>
    </>
  );
}
