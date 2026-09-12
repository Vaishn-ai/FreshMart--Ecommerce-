import { useCallback, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { MdAdd, MdDelete, MdEdit, MdRefresh, MdSave, MdClose } from "react-icons/md";
import api from "../services/api";
import SEO from "../components/SEO.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";

const EMPTY_FORM = {
  name: "",
  category: "",
  brand: "",
  description: "",
  highlights: "",
  specifications: "",
  nutrition_facts: "",
  unit: "pcs",
  weight_or_size: "",
  color: "",
  mrp: "",
  discount_price: "",
  stock: "0",
  sku: "",
  barcode: "",
  is_featured: false,
  is_flash_sale: false,
  flash_sale_ends_at: "",
  is_active: true,
  image_alt_text: "",
  primary_image: null,
};

const UNITS = [
  ["kg", "Kg"],
  ["g", "Gram"],
  ["l", "Litre"],
  ["ml", "ml"],
  ["pcs", "Pieces"],
  ["pack", "Pack"],
];

function parseJson(value, fallback) {
  if (!value.trim()) return fallback;
  return JSON.parse(value);
}

function formatDateTimeLocal(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

export default function ProductManager() {
  const { user, loading: authLoading } = useAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const flatCategories = useMemo(() => {
    const result = [];
    categories.forEach((category) => {
      result.push(category);
      (category.subcategories || []).forEach((child) => result.push(child));
    });
    return result;
  }, [categories]);

  const loadCatalog = useCallback(async () => {
    if (!user?.is_superuser) return;
    setLoading(true);
    try {
      const [productsResponse, categoriesResponse, brandsResponse] = await Promise.all([
        api.get("/products/manage/"),
        api.get("/categories/"),
        api.get("/brands/"),
      ]);

      setProducts(Array.isArray(productsResponse.data) ? productsResponse.data : []);
      setCategories(categoriesResponse.data?.results || categoriesResponse.data || []);
      setBrands(brandsResponse.data?.results || brandsResponse.data || []);
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Unable to load catalog manager");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const updateField = (event) => {
    const { name, value, type, checked, files } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : name === "primary_image" ? files?.[0] || null : value,
    }));
  };

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
  };

  const editProduct = async (id) => {
    try {
      const { data } = await api.get(`/products/${id}/manage-detail/`);
      setEditingId(id);
      setForm({
        name: data.name || "",
        category: data.category?.id || "",
        brand: data.brand?.id || "",
        description: data.description || "",
        highlights: Array.isArray(data.highlights) ? data.highlights.join(", ") : "",
        specifications: data.specifications && Object.keys(data.specifications).length
          ? JSON.stringify(data.specifications, null, 2)
          : "",
        nutrition_facts: data.nutrition_facts && Object.keys(data.nutrition_facts).length
          ? JSON.stringify(data.nutrition_facts, null, 2)
          : "",
        unit: data.unit || "pcs",
        weight_or_size: data.weight_or_size || "",
        color: data.color || "",
        mrp: data.mrp ?? "",
        discount_price: data.discount_price ?? "",
        stock: data.stock ?? 0,
        sku: data.sku || "",
        barcode: data.barcode || "",
        is_featured: Boolean(data.is_featured),
        is_flash_sale: Boolean(data.is_flash_sale),
        flash_sale_ends_at: formatDateTimeLocal(data.flash_sale_ends_at),
        is_active: Boolean(data.is_active ?? true),
        image_alt_text: data.images?.find((image) => image.is_primary)?.alt_text || "",
        primary_image: null,
      });
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error(error);
      toast.error("Unable to load product details");
    }
  };

  const deleteProduct = async (id, name) => {
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;

    try {
      await api.delete(`/products/${id}/`);
      toast.success("Product deleted");
      if (editingId === id) resetForm();
      await loadCatalog();
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Could not delete product");
    }
  };

  const saveProduct = async (event) => {
    event.preventDefault();
    if (!user?.is_superuser) return;

    if (!form.name.trim() || !form.category || !form.mrp || !form.discount_price || !form.sku.trim()) {
      toast.error("Please fill name, category, MRP, discount price and SKU");
      return;
    }

    let specifications = {};
    let nutritionFacts = {};

    try {
      specifications = parseJson(form.specifications, {});
      nutritionFacts = parseJson(form.nutrition_facts, {});
      if (typeof specifications !== "object" || Array.isArray(specifications)) {
        throw new Error("Specifications must be a JSON object");
      }
      if (typeof nutritionFacts !== "object" || Array.isArray(nutritionFacts)) {
        throw new Error("Nutrition facts must be a JSON object");
      }
    } catch (error) {
      toast.error(error.message || "Invalid JSON in specifications or nutrition facts");
      return;
    }

    const payload = new FormData();
    payload.append("name", form.name.trim());
    payload.append("category", form.category);
    if (form.brand) payload.append("brand", form.brand);
    payload.append("description", form.description);
    payload.append(
      "highlights",
      JSON.stringify(form.highlights.split(",").map((item) => item.trim()).filter(Boolean))
    );
    payload.append("specifications", JSON.stringify(specifications));
    payload.append("nutrition_facts", JSON.stringify(nutritionFacts));
    payload.append("unit", form.unit);
    payload.append("weight_or_size", form.weight_or_size);
    payload.append("color", form.color);
    payload.append("mrp", form.mrp);
    payload.append("discount_price", form.discount_price);
    payload.append("stock", form.stock || "0");
    payload.append("sku", form.sku.trim());
    payload.append("barcode", form.barcode);
    payload.append("is_featured", String(form.is_featured));
    payload.append("is_flash_sale", String(form.is_flash_sale));
    payload.append("is_active", String(form.is_active));
    if (form.flash_sale_ends_at) payload.append("flash_sale_ends_at", new Date(form.flash_sale_ends_at).toISOString());
    if (form.primary_image) payload.append("primary_image", form.primary_image);
    payload.append("image_alt_text", form.image_alt_text);

    setSaving(true);
    try {
      if (editingId) {
        await api.put(`/products/${editingId}/`, payload);
        toast.success("Product updated");
      } else {
        await api.post("/products/", payload);
        toast.success("Product added");
      }
      resetForm();
      await loadCatalog();
    } catch (error) {
      console.error(error);
      const data = error.response?.data;
      const message = typeof data === "object"
        ? Object.entries(data).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`).join(" | ")
        : "Could not save product";
      toast.error(message || "Could not save product");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading) {
    return <div className="max-w-3xl mx-auto px-4 py-16 text-center text-gray-500">Checking access...</div>;
  }

  if (!user?.is_superuser) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <SEO title="Access denied" path="/manage-products" noindex />
        <div className="card p-8">
          <h1 className="text-2xl font-bold mb-2">Superuser access only</h1>
          <p className="text-gray-500">This catalog manager is available only to the FreshMart superuser.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <SEO title="Manage Products" path="/manage-products" noindex />

      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <p className="text-sm text-primary font-semibold">SUPERUSER</p>
          <h1 className="text-2xl font-bold">Manage Products</h1>
          <p className="text-sm text-gray-500 mt-1">Add, edit, feature, deactivate, or delete products without opening Django Admin.</p>
        </div>
        <button type="button" onClick={loadCatalog} className="px-4 py-2 rounded-full border flex items-center gap-2">
          <MdRefresh /> Refresh
        </button>
      </div>

      <div className="grid lg:grid-cols-[minmax(0,1fr)_420px] gap-6 items-start">
        <section className="card p-5">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold">{editingId ? "Edit product" : "Add product"}</h2>
            {editingId && (
              <button type="button" onClick={resetForm} className="text-sm text-gray-500 flex items-center gap-1">
                <MdClose /> Cancel edit
              </button>
            )}
          </div>

          <form onSubmit={saveProduct} className="space-y-5">
            <div className="grid sm:grid-cols-2 gap-4">
              <Field label="Product name" name="name" value={form.name} onChange={updateField} required />
              <Field label="SKU" name="sku" value={form.sku} onChange={updateField} required />
              <SelectField label="Category" name="category" value={form.category} onChange={updateField} options={flatCategories} required />
              <SelectField label="Brand" name="brand" value={form.brand} onChange={updateField} options={brands} allowEmpty />
              <SelectField label="Unit" name="unit" value={form.unit} onChange={updateField} options={UNITS.map(([value, label]) => ({ id: value, name: label }))} />
              <Field label="Weight / Size" name="weight_or_size" value={form.weight_or_size} onChange={updateField} placeholder="e.g. 500g, 1L" />
              <Field label="MRP" name="mrp" type="number" step="0.01" min="0" value={form.mrp} onChange={updateField} required />
              <Field label="Discount price" name="discount_price" type="number" step="0.01" min="0" value={form.discount_price} onChange={updateField} required />
              <Field label="Stock" name="stock" type="number" min="0" value={form.stock} onChange={updateField} />
              <Field label="Barcode" name="barcode" value={form.barcode} onChange={updateField} />
              <Field label="Color" name="color" value={form.color} onChange={updateField} />
              <Field label="Image alt text" name="image_alt_text" value={form.image_alt_text} onChange={updateField} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea name="description" value={form.description} onChange={updateField} rows={3} className="w-full rounded-xl border border-gray-300 px-3 py-2" />
            </div>

            <Field
              label="Highlights (comma separated)"
              name="highlights"
              value={form.highlights}
              onChange={updateField}
              placeholder="Rich in protein, Farm sourced"
            />

            <div className="grid md:grid-cols-2 gap-4">
              <JsonField label="Specifications JSON" name="specifications" value={form.specifications} onChange={updateField} placeholder={'{"Origin":"India"}'} />
              <JsonField label="Nutrition facts JSON" name="nutrition_facts" value={form.nutrition_facts} onChange={updateField} placeholder={'{"Calories":"52 kcal"}'} />
            </div>

            <div className="grid sm:grid-cols-2 gap-3">
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="is_featured" checked={form.is_featured} onChange={updateField} /> Featured product</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="is_flash_sale" checked={form.is_flash_sale} onChange={updateField} /> Flash sale</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="is_active" checked={form.is_active} onChange={updateField} /> Active / visible</label>
            </div>

            {form.is_flash_sale && (
              <Field label="Flash sale ends" name="flash_sale_ends_at" type="datetime-local" value={form.flash_sale_ends_at} onChange={updateField} />
            )}

            <div>
              <label className="block text-sm font-medium mb-1">Primary product image</label>
              <input type="file" name="primary_image" accept="image/*" onChange={updateField} className="w-full text-sm" />
              {editingId && <p className="text-xs text-gray-500 mt-1">Leave empty to keep the current image.</p>}
            </div>

            <button type="submit" disabled={saving} className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-60">
              {editingId ? <MdSave /> : <MdAdd />}
              {saving ? "Saving..." : editingId ? "Update product" : "Add product"}
            </button>
          </form>
        </section>

        <section className="card p-5 lg:sticky lg:top-24">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Existing products</h2>
            <span className="text-sm text-gray-500">{products.length} total</span>
          </div>

          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, index) => <div key={index} className="h-16 rounded-xl bg-gray-100 animate-pulse" />)}
            </div>
          ) : products.length === 0 ? (
            <p className="text-sm text-gray-500 py-8 text-center">No products found.</p>
          ) : (
            <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
              {products.map((product) => (
                <div key={product.id} className="border rounded-xl p-3 flex items-center gap-3">
                  <div className="w-14 h-14 rounded-lg bg-gray-100 overflow-hidden shrink-0">
                    {product.primary_image ? <img src={product.primary_image} alt="" className="w-full h-full object-cover" /> : null}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-sm truncate">{product.name}</p>
                    <p className="text-xs text-gray-500">₹{product.discount_price} · {product.in_stock ? "In stock" : "Out of stock"}</p>
                    <div className="flex gap-1 mt-1">
                      {product.is_featured && <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded">Featured</span>}
                      {product.is_flash_sale && <span className="text-[10px] bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded">Flash</span>}
                      {!product.in_stock && <span className="text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded">Out</span>}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button type="button" onClick={() => editProduct(product.id)} className="p-2 rounded-lg hover:bg-gray-100" aria-label={`Edit ${product.name}`}><MdEdit /></button>
                    <button type="button" onClick={() => deleteProduct(product.id, product.name)} className="p-2 rounded-lg hover:bg-red-50 text-red-500" aria-label={`Delete ${product.name}`}><MdDelete /></button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function Field({ label, name, value, onChange, type = "text", placeholder = "", required = false, step, min }) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium mb-1">{label}{required ? " *" : ""}</label>
      <input id={name} name={name} type={type} value={value} onChange={onChange} placeholder={placeholder} required={required} step={step} min={min} className="w-full rounded-xl border border-gray-300 px-3 py-2" />
    </div>
  );
}

function JsonField({ label, name, value, onChange, placeholder }) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium mb-1">{label}</label>
      <textarea id={name} name={name} value={value} onChange={onChange} rows={6} placeholder={placeholder} className="w-full rounded-xl border border-gray-300 px-3 py-2 font-mono text-xs" />
    </div>
  );
}

function SelectField({ label, name, value, onChange, options, required = false, allowEmpty = false }) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium mb-1">{label}{required ? " *" : ""}</label>
      <select id={name} name={name} value={value} onChange={onChange} required={required} className="w-full rounded-xl border border-gray-300 px-3 py-2">
        {allowEmpty && <option value="">No brand</option>}
        {!allowEmpty && !required && <option value="">Select...</option>}
        {options.map((option) => <option key={option.id} value={option.id}>{option.name}</option>)}
      </select>
    </div>
  );
}
