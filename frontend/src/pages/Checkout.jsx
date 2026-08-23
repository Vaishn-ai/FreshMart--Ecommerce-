import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../services/api";
import SEO from "../components/SEO.jsx";
import { useCart } from "../contexts/CartContext.jsx";

export default function Checkout() {
  const { cart, refreshCart } = useCart();
  const [addresses, setAddresses] = useState([]);
  const [addressId, setAddressId] = useState("");
  const [shippingMethod, setShippingMethod] = useState("standard");
  const [paymentMethod, setPaymentMethod] = useState("cod");
  const [placing, setPlacing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAddresses = async () => {
      try {
        const response = await api.get("/auth/addresses/");

        console.log("Address API:", response.data);

        const addressList = Array.isArray(response.data)
          ? response.data
          : response.data.results || [];

        setAddresses(addressList);

        const defaultAddress =
          addressList.find((a) => a.is_default) || addressList[0];

        if (defaultAddress) {
          setAddressId(defaultAddress.id);
        }
      } catch (error) {
        console.error(error);
        toast.error("Unable to load addresses");
        setAddresses([]);
      }
    };

    fetchAddresses();
  }, []);

  const placeOrder = async () => {
    if (!addressId) return toast.error("Please select a delivery address");
    setPlacing(true);
    try {
      const { data: order } = await api.post("/orders/checkout/", {
        address_id: addressId,
        shipping_method: shippingMethod,
        payment_method: paymentMethod,
      });

      if (paymentMethod === "razorpay") {
        const { data: rp } = await api.post(`/payments/razorpay/create/${order.id}/`);
        toast("Razorpay checkout would open here with order " + rp.razorpay_order_id);
      } else if (paymentMethod === "stripe") {
        const { data: intent } = await api.post(`/payments/stripe/create-intent/${order.id}/`);
        toast("Stripe Elements would confirm client_secret here.");
      } else if (paymentMethod === "upi") {
        const { data: upi } = await api.post("/payments/upi/initiate/", { order_id: order.id, upi_id: "" });
        toast(upi.detail);
      } else {
        toast.success(`Order ${order.order_number} placed!`);
      }

      refreshCart();
      navigate("/orders");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Checkout failed");
    } finally {
      setPlacing(false);
    }
  };

  if (!cart) return null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <SEO title="Checkout" path="/checkout" noindex />
      <h1 className="text-xl font-semibold">Checkout</h1>

      <section className="card p-4">
        <h2 className="font-semibold mb-3">Delivery address</h2>
        {addresses.length === 0 ? (
          <p className="text-sm text-gray-500">No saved addresses — add one from your profile first.</p>
        ) : (
          <div className="space-y-2" role="radiogroup" aria-label="Delivery address">
            {addresses.map((a) => (
              <label key={a.id} className="flex items-start gap-2 border border-gray-200 rounded-xl p-3 cursor-pointer">
                <input type="radio" name="address" checked={addressId === a.id} onChange={() => setAddressId(a.id)} className="mt-1" />
                <span className="text-sm">
                  <strong>{a.full_name}</strong> — {a.line1}, {a.city}, {a.state} {a.pincode}
                </span>
              </label>
            ))}
          </div>
        )}
      </section>

      <section className="card p-4">
        <h2 className="font-semibold mb-3">Shipping method</h2>
        <div className="flex gap-4">
          {["standard", "express"].map((m) => (
            <label key={m} className="flex items-center gap-2 text-sm capitalize">
              <input type="radio" name="shipping" checked={shippingMethod === m} onChange={() => setShippingMethod(m)} />
              {m}
            </label>
          ))}
        </div>
      </section>

      <section className="card p-4">
        <h2 className="font-semibold mb-3">Payment method</h2>
        <div className="grid grid-cols-2 gap-3">
          {[["cod", "Cash on Delivery"], ["razorpay", "Razorpay"], ["stripe", "Stripe (Card)"], ["upi", "UPI"]].map(([val, label]) => (
            <label key={val} className="flex items-center gap-2 text-sm border border-gray-200 rounded-xl p-3 cursor-pointer">
              <input type="radio" name="payment" checked={paymentMethod === val} onChange={() => setPaymentMethod(val)} />
              {label}
            </label>
          ))}
        </div>
      </section>

      <section className="card p-4">
        <h2 className="font-semibold mb-3">Order total</h2>
        <p className="text-2xl font-bold">₹{cart.total}</p>
      </section>

      <button onClick={placeOrder} disabled={placing} className="btn-primary w-full disabled:opacity-60">
        {placing ? "Placing order..." : "Place order"}
      </button>
    </div>
  );
}
