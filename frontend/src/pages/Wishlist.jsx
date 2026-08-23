import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import SEO from "../components/SEO.jsx";
import { useCart } from "../contexts/CartContext.jsx";

export default function Wishlist() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const { refreshCart } = useCart();

  const fetchWishlist = async () => {
    setLoading(true);
    const { data } = await api.get("/wishlist/");
    setItems(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchWishlist();
  }, []);

  const remove = async (productId) => {
    await api.delete(`/wishlist/${productId}/`);
    setItems((prev) => prev.filter((i) => i.product !== productId));
  };

  const moveToCart = async (productId) => {
    try {
      await api.post(`/wishlist/${productId}/move-to-cart/`);
      setItems((prev) => prev.filter((i) => i.product !== productId));
      refreshCart();
      toast.success("Moved to cart");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not move to cart");
    }
  };

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-16 text-center text-gray-400">Loading...</div>;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <SEO title="Your Wishlist" path="/wishlist" noindex />
      <h1 className="text-xl font-semibold mb-6">Your Wishlist ({items.length})</h1>
      {items.length === 0 ? (
        <p className="text-gray-500">Nothing here yet — tap the heart icon on any product to save it.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {items.map((item) => {
            const product = item.product_detail;
            return (
              <div key={item.id} className="card p-3">
                <div className="aspect-square rounded-xl bg-gray-50 overflow-hidden mb-2">
                  {product.primary_image ? (
                    <img
                      src={product.primary_image}
                      alt={product.name}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-300 text-xs">
                      No image
                    </div>
                  )}
                </div>
                <p className="text-sm font-medium line-clamp-2">{product.name}</p>
                <p className="text-sm font-semibold mb-2">₹{product.discount_price}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => moveToCart(item.product)}
                    className="btn-primary !px-3 !py-1.5 text-xs flex-1"
                  >
                    Move to cart
                  </button>
                  <button
                    onClick={() => remove(item.product)}
                    className="text-xs text-gray-400 hover:text-red-500 px-2"
                  >
                    Remove
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
