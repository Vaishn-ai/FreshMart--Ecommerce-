import { useEffect, useState } from "react";
import {
  FaPlus,
  FaEdit,
  FaTrash,
  FaMapMarkerAlt,
} from "react-icons/fa";
import toast from "react-hot-toast";
import api from "../services/api";
import SEO from "../components/SEO";

const initialForm = {
  full_name: "",
  phone: "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  pincode: "",
  country: "India",
  label: "home",
  landmark: "",
  is_default: false,
};

export default function Address() {
  const [addresses, setAddresses] = useState([]);
  const [form, setForm] = useState({ ...initialForm });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchAddresses();
  }, []);

  const fetchAddresses = async () => {
    try {
      const { data } = await api.get("/auth/addresses/");
      setAddresses(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      console.error(err);
      toast.error("Unable to load addresses.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = ({ target }) => {
    const { name, value, type, checked } = target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const resetForm = () => {
    setEditingId(null);
    setForm({ ...initialForm });
  };

  const saveAddress = async (e) => {
    e.preventDefault();

    setSaving(true);

    try {
      if (editingId) {
        await api.put(`/auth/addresses/${editingId}/`, form);
        toast.success("Address updated successfully.");
      } else {
        await api.post("/auth/addresses/", form);
        toast.success("Address added successfully.");
      }

      resetForm();
      fetchAddresses();
    } catch (err) {
      console.error(err);
      toast.error("Unable to save address.");
    } finally {
      setSaving(false);
    }
  };

  const editAddress = (address) => {
    setEditingId(address.id);

    setForm({
      full_name: address.full_name || "",
      phone: address.phone || "",
      line1: address.line1 || "",
      line2: address.line2 || "",
      city: address.city || "",
      state: address.state || "",
      pincode: address.pincode || "",
      country: address.country || "India",
      label: address.label || "home",
      landmark: address.landmark || "",
      is_default: !!address.is_default,
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const deleteAddress = async (id) => {
    if (!window.confirm("Delete this address?")) return;

    try {
      await api.delete(`/auth/addresses/${id}/`);
      toast.success("Address deleted.");
      fetchAddresses();

      if (editingId === id) {
        resetForm();
      }
    } catch (err) {
      console.error(err);
      toast.error("Unable to delete address.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">

      <SEO title="My Addresses" path="/profile/address" noindex />

      <h1 className="text-3xl font-bold mb-8">
        Delivery Addresses
      </h1>

      <div className="grid lg:grid-cols-2 gap-8">

        {/* FORM */}

        <div className="card rounded-xl shadow p-6">

          <h2 className="text-xl font-semibold flex items-center gap-2 mb-6">
            <FaPlus />
            {editingId ? "Edit Address" : "Add New Address"}
          </h2>

          <form
            onSubmit={saveAddress}
            className="space-y-4"
          >

            <input
              className="input w-full"
              placeholder="Full Name"
              name="full_name"
              value={form.full_name || ""}
              onChange={handleChange}
              required
            />

            <input
              className="input w-full"
              placeholder="Phone Number"
              name="phone"
              value={form.phone || ""}
              onChange={handleChange}
              required
            />

            <input
              className="input w-full"
              placeholder="House / Flat / Building"
              name="line1"
              value={form.line1 || ""}
              onChange={handleChange}
              required
            />

            <input
              className="input w-full"
              placeholder="Area / Street"
              name="line2"
              value={form.line2 || ""}
              onChange={handleChange}
            />

            <input
              className="input w-full"
              placeholder="Landmark"
              name="landmark"
              value={form.landmark || ""}
              onChange={handleChange}
            />

            <div className="grid grid-cols-2 gap-4">

              <input
                className="input"
                placeholder="City"
                name="city"
                value={form.city || ""}
                onChange={handleChange}
                required
              />

              <input
                className="input"
                placeholder="State"
                name="state"
                value={form.state || ""}
                onChange={handleChange}
                required
              />

            </div>

            <div className="grid grid-cols-2 gap-4">

              <input
                className="input"
                placeholder="Pincode"
                name="pincode"
                value={form.pincode || ""}
                onChange={handleChange}
                required
              />

              <input
                className="input"
                placeholder="Country"
                name="country"
                value={form.country || ""}
                onChange={handleChange}
              />

            </div>

            <select
              className="input w-full"
              name="label"
              value={form.label || "home"}
              onChange={handleChange}
            >
              <option value="home">Home</option>
              <option value="work">Work</option>
              <option value="other">Other</option>
            </select>

            <label className="flex items-center gap-2">

              <input
                type="checkbox"
                name="is_default"
                checked={!!form.is_default}
                onChange={handleChange}
              />

              Set as default address

            </label>

            <div className="flex gap-3">

              <button
                type="submit"
                disabled={saving}
                className="btn-primary"
              >
                {saving
                  ? "Saving..."
                  : editingId
                  ? "Update Address"
                  : "Save Address"}
              </button>

              {editingId && (
                <button
                  type="button"
                  onClick={resetForm}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              )}

            </div>

          </form>

        </div>
                {/* ADDRESS LIST */}

        <div>

          <h2 className="text-xl font-semibold mb-6">
            Saved Addresses
          </h2>

          {loading ? (

            <div className="card rounded-xl p-8 text-center">
              Loading addresses...
            </div>

          ) : addresses.length === 0 ? (

            <div className="card rounded-xl p-8 text-center">

              <FaMapMarkerAlt
                className="mx-auto text-5xl text-gray-400 mb-4"
              />

              <h3 className="text-lg font-semibold mb-2">
                No Addresses Found
              </h3>

              <p className="text-gray-500">
                Add your first delivery address.
              </p>

            </div>

          ) : (

            <div className="space-y-5">

              {addresses.map((address) => (

                <div
                  key={address.id}
                  className="card rounded-xl shadow-md border p-5 hover:shadow-lg transition"
                >

                  <div className="flex justify-between items-start">

                    <div className="flex-1">

                      <div className="flex items-center gap-3 flex-wrap">

                        <h3 className="text-lg font-semibold">
                          {address.full_name}
                        </h3>

                        <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 capitalize">
                          {address.label}
                        </span>

                        {address.is_default && (
                          <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                            Default
                          </span>
                        )}

                      </div>

                      <p className="text-sm text-gray-600 mt-2">
                        📞 {address.phone}
                      </p>

                      <p className="mt-3 text-gray-700 leading-7">

                        {address.line1}

                        {address.line2 && (
                          <>
                            <br />
                            {address.line2}
                          </>
                        )}

                        {address.landmark && (
                          <>
                            <br />
                            Landmark: {address.landmark}
                          </>
                        )}

                        <br />

                        {address.city}, {address.state}

                        <br />

                        {address.pincode}

                        <br />

                        {address.country}

                      </p>

                    </div>

                    <div className="flex flex-col gap-3 ml-4">

                      <button
                        onClick={() => editAddress(address)}
                        className="text-blue-600 hover:text-blue-800 transition"
                        title="Edit Address"
                      >
                        <FaEdit size={18} />
                      </button>

                      <button
                        onClick={() => deleteAddress(address.id)}
                        className="text-red-600 hover:text-red-800 transition"
                        title="Delete Address"
                      >
                        <FaTrash size={18} />
                      </button>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </div>
  );
}