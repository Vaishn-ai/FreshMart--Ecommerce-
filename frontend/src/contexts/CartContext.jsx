import { createContext, useContext, useState, useCallback, useEffect } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { useAuth } from "./AuthContext.jsx";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);

  const refreshCart = useCallback(async () => {
    if (!user) return setCart(null);
    setLoading(true);
    try {
      const { data } = await api.get("/cart/");
      setCart(data);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const addToCart = async (productId, quantity = 1, variantId = null) => {
    try {
      const { data } = await api.post("/cart/add/", { product_id: productId, variant_id: variantId, quantity });
      setCart(data);
      toast.success("Added to cart");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not add to cart");
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    try {
      const { data } = await api.patch(`/cart/items/${itemId}/`, { quantity });
      setCart(data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not update quantity");
    }
  };

  const removeItem = async (itemId) => {
    const { data } = await api.delete(`/cart/items/${itemId}/`);
    setCart(data);
  };

  const saveForLater = async (itemId) => {
    const { data } = await api.post(`/cart/items/${itemId}/save-for-later/`);
    setCart(data);
  };

  const moveToCart = async (itemId) => {
    const { data } = await api.delete(`/cart/items/${itemId}/save-for-later/`);
    setCart(data);
  };

  const applyCoupon = async (code) => {
    try {
      const { data } = await api.post("/cart/coupon/", { code });
      setCart(data);
      toast.success("Coupon applied");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Invalid coupon");
    }
  };

  const removeCoupon = async () => {
    const { data } = await api.delete("/cart/coupon/");
    setCart(data);
  };

  return (
    <CartContext.Provider
      value={{ cart, loading, refreshCart, addToCart, updateQuantity, removeItem, saveForLater, moveToCart, applyCoupon, removeCoupon }}
    >
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
