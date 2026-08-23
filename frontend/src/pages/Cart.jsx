import { useState } from "react";
import { Link } from "react-router-dom";
import { MdDelete, MdBookmarkBorder } from "react-icons/md";
import SEO from "../components/SEO.jsx";
import { useCart } from "../contexts/CartContext.jsx";

export default function Cart() {
  const { cart, updateQuantity, removeItem, saveForLater, moveToCart, applyCoupon, removeCoupon } = useCart();
  const [couponInput, setCouponInput] = useState("");

  if (!cart) return (
    <>
      <SEO title="Your Cart" path="/cart" noindex />
      <div className="max-w-3xl mx-auto px-4 py-16 text-center text-gray-400">Loading your cart...</div>
    </>
  );

  if (cart.items.length === 0 && cart.saved_items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <SEO title="Your Cart" path="/cart" noindex />
        <p className="text-gray-500 mb-4">Your cart is empty.</p>
        <Link to="/products" className="btn-primary">Start shopping</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 grid md:grid-cols-3 gap-8">
      <SEO title="Your Cart" path="/cart" noindex />
      <div className="md:col-span-2 space-y-4">
        <h1 className="text-xl font-semibold">Your Cart ({cart.items.length})</h1>
        {cart.items.map((item) => (
          <div key={item.id} className="card flex gap-4 p-3">
            <img
              src={item.product_detail.primary_image}
              alt={item.product_detail.name}
              className="w-20 h-20 rounded-xl object-cover bg-gray-50"
            />
            <div className="flex-1">
              <p className="font-medium">{item.product_detail.name}</p>
              <p className="text-sm text-gray-500">₹{item.unit_price} each</p>
              <div className="flex items-center gap-2 mt-2">
                <label htmlFor={`qty-${item.id}`} className="sr-only">Quantity</label>
                <input
                  id={`qty-${item.id}`}
                  type="number"
                  min={1}
                  max={item.available_stock}
                  value={item.quantity}
                  onChange={(e) => updateQuantity(item.id, Number(e.target.value))}
                  className="w-16 border border-gray-300 rounded-lg px-2 py-1 text-sm"
                />
                <button onClick={() => saveForLater(item.id)} aria-label="Save for later" className="text-gray-400 hover:text-primary p-1">
                  <MdBookmarkBorder size={18} />
                </button>
                <button onClick={() => removeItem(item.id)} aria-label="Remove item" className="text-gray-400 hover:text-red-500 p-1">
                  <MdDelete size={18} />
                </button>
              </div>
            </div>
            <p className="font-semibold">₹{item.line_total}</p>
          </div>
        ))}

        {cart.saved_items.length > 0 && (
          <section className="mt-8">
            <h2 className="font-semibold mb-3">Saved for later ({cart.saved_items.length})</h2>
            {cart.saved_items.map((item) => (
              <div key={item.id} className="card flex gap-4 p-3 mb-2">
                <img src={item.product_detail.primary_image} alt={item.product_detail.name} className="w-16 h-16 rounded-xl object-cover bg-gray-50" />
                <div className="flex-1">
                  <p className="font-medium text-sm">{item.product_detail.name}</p>
                  <button onClick={() => moveToCart(item.id)} className="text-primary text-sm mt-1">Move to cart</button>
                </div>
              </div>
            ))}
          </section>
        )}
      </div>

      <aside className="card p-4 h-fit">
        <h2 className="font-semibold mb-4">Order Summary</h2>

        <div className="flex gap-2 mb-4">
          <label htmlFor="coupon" className="sr-only">Coupon code</label>
          <input
            id="coupon"
            value={couponInput}
            onChange={(e) => setCouponInput(e.target.value)}
            placeholder="Coupon code"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
          <button onClick={() => applyCoupon(couponInput)} className="text-sm px-3 py-2 rounded-lg border border-primary text-primary">
            Apply
          </button>
        </div>
        {cart.coupon_code && (
          <div className="flex justify-between text-sm text-primary mb-3">
            <span>Coupon: {cart.coupon_code}</span>
            <button onClick={removeCoupon} className="underline">Remove</button>
          </div>
        )}

        <dl className="space-y-2 text-sm">
          <div className="flex justify-between"><dt>Subtotal</dt><dd>₹{cart.subtotal}</dd></div>
          <div className="flex justify-between"><dt>Discount</dt><dd>-₹{cart.discount_amount}</dd></div>
          <div className="flex justify-between"><dt>Delivery</dt><dd>₹{cart.delivery_charge}</dd></div>
          <div className="flex justify-between"><dt>Tax (GST)</dt><dd>₹{cart.tax_amount}</dd></div>
          <div className="flex justify-between font-semibold text-base border-t border-gray-100 pt-2 mt-2">
            <dt>Total</dt><dd>₹{cart.total}</dd>
          </div>
        </dl>

        <Link to="/checkout" className="btn-primary w-full text-center block mt-4">Proceed to checkout</Link>
      </aside>
    </div>
  );
}
