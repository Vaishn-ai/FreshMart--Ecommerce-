import { useEffect, useState } from "react";
import api from "../services/api";
import SEO from "../components/SEO.jsx";

const STATUS_STEPS = [
  { key: "pending", label: "Ordered" },
  { key: "confirmed", label: "Confirmed" },
  { key: "packed", label: "Packed" },
  { key: "shipped", label: "Out for Delivery" },
  { key: "delivered", label: "Delivered" },
];

const getStatusBadge = (status) => {
  switch (status) {
    case "pending":
      return {
        text: "📝 Ordered",
        className: "bg-yellow-100 text-yellow-700",
      };

    case "confirmed":
      return {
        text: "✅ Confirmed",
        className: "bg-blue-100 text-blue-700",
      };

    case "packed":
      return {
        text: "📦 Packed",
        className: "bg-indigo-100 text-indigo-700",
      };

    case "shipped":
      return {
        text: "🚚 Out for Delivery",
        className: "bg-purple-100 text-purple-700",
      };

    case "delivered":
      return {
        text: "🎉 Delivered",
        className: "bg-green-100 text-green-700",
      };

    case "cancelled":
      return {
        text: "❌ Cancelled",
        className: "bg-red-100 text-red-700",
      };

    case "returned":
      return {
        text: "↩️ Returned",
        className: "bg-gray-100 text-gray-700",
      };

    default:
      return {
        text: status,
        className: "bg-gray-100 text-gray-700",
      };
  }
};

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const { data } = await api.get("/orders/");
      setOrders(data.results || data);
    } catch (error) {
      console.error("Failed to load orders:", error);
    } finally {
      setLoading(false);
    }
  };

  const cancelOrder = async (id) => {
    if (!window.confirm("Are you sure you want to cancel this order?")) {
      return;
    }

    try {
      const { data } = await api.post(`/orders/${id}/cancel/`);

      setOrders((prev) =>
        prev.map((order) => (order.id === id ? data : order))
      );
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
          JSON.stringify(error.response?.data) ||
          "Unable to cancel order."
      );
    }
  };

  const downloadInvoice = async (order) => {
    try {
      setDownloadingId(order.id);

      const response = await api.get(
        `/orders/${order.id}/invoice/`,
        {
          responseType: "blob",
        }
      );

      const blob = new Blob([response.data], {
        type: "application/pdf",
      });

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = url;
      link.download = `Invoice-${order.order_number}.pdf`;

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert("Unable to download invoice.");
    } finally {
      setDownloadingId(null);
    }
  };

  if (loading) {
    return (
      <>
        <SEO title="Your Orders" path="/orders" noindex />

        <div className="max-w-4xl mx-auto py-20 text-center text-gray-500">
          Loading your orders...
        </div>
      </>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <SEO title="Your Orders" path="/orders" noindex />

      <h1 className="text-3xl font-bold mb-8">
        My Orders
      </h1>

      {orders.length === 0 ? (
        <div className="card p-10 rounded-xl text-center">
          <h2 className="text-xl font-semibold mb-2">
            No Orders Yet
          </h2>

          <p className="text-gray-500">
            Start shopping to see your orders here.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => {
            const stepIndex = STATUS_STEPS.findIndex(
              (step) => step.key === order.status
            );

            const badge = getStatusBadge(order.status);
                        return (
              <div
                key={order.id}
                className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 hover:shadow-md transition"
              >
                {/* Header */}
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
                  <div>
                    <h2 className="text-lg font-bold">
                      {order.order_number}
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                      Ordered on{" "}
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="text-left md:text-right">
                    <p className="text-2xl font-bold text-primary">
                      ₹{order.total}
                    </p>

                    <span
                      className={`inline-flex mt-2 px-3 py-1 rounded-full text-xs font-semibold ${badge.className}`}
                    >
                      {badge.text}
                    </span>
                  </div>
                </div>

                {/* Progress */}
                {order.status !== "cancelled" &&
                  order.status !== "returned" && (
                    <div className="mb-6">
                      <div className="flex justify-between text-[11px] mb-3">
                        {STATUS_STEPS.map((step, index) => (
                          <span
                            key={step.key}
                            className={
                              index <= stepIndex
                                ? "font-semibold text-primary"
                                : "text-gray-400"
                            }
                          >
                            {step.label}
                          </span>
                        ))}
                      </div>

                      <div className="flex gap-2">
                        {STATUS_STEPS.map((step, index) => (
                          <div
                            key={step.key}
                            className={`flex-1 h-2 rounded-full transition-all ${
                              index <= stepIndex
                                ? "bg-primary"
                                : "bg-gray-200"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                {/* Products */}
                <div className="border rounded-xl divide-y mb-6">
                  {order.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex justify-between items-center px-4 py-3"
                    >
                      <div>
                        <h3 className="font-medium">
                          {item.product_name}
                        </h3>

                        <p className="text-xs text-gray-500">
                          Quantity: {item.quantity}
                        </p>
                      </div>

                      <div className="font-semibold">
                        ₹
                        {(
                          Number(item.unit_price) *
                          Number(item.quantity)
                        ).toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 text-sm">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-gray-500">Subtotal</p>
                    <p className="font-semibold">
                      ₹{order.subtotal}
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-gray-500">Delivery</p>
                    <p className="font-semibold">
                      ₹{order.delivery_charge}
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-gray-500">Tax</p>
                    <p className="font-semibold">
                      ₹{order.tax}
                    </p>
                  </div>

                  <div className="bg-primary/10 rounded-lg p-3">
                    <p className="text-gray-500">Total</p>
                    <p className="font-bold text-primary">
                      ₹{order.total}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => downloadInvoice(order)}
                    disabled={downloadingId === order.id}
                    className="px-5 py-2 rounded-lg border border-primary text-primary hover:bg-primary hover:text-white transition disabled:opacity-60"
                  >
                    {downloadingId === order.id
                      ? "Downloading..."
                      : "📄 Download Invoice"}
                  </button>

                  {["pending", "confirmed", "packed"].includes(
                    order.status
                  ) && (
                    <button
                      onClick={() => cancelOrder(order.id)}
                      className="px-5 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition"
                    >
                      ❌ Cancel Order
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}