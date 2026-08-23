import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../services/api";
import ProductCard from "../components/ProductCard.jsx";
import SEO from "../components/SEO.jsx";
import { useCart } from "../contexts/CartContext.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";
import toast from "react-hot-toast";

export default function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState({ results: [], count: 0, next: null, previous: null });
  const [loading, setLoading] = useState(true);
  const { addToCart } = useCart();
  const { user } = useAuth();

  const search = searchParams.get("search") || "";
  const ordering = searchParams.get("ordering") || "";
  const page = searchParams.get("page") || "1";
  const category = searchParams.get("category") || "";

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/products/", {
        params: {
          search,
          category,
          ordering,
          page,
        },
      });

      setData(data);
    } finally {
      setLoading(false);
    }
  }, [search, category, ordering, page]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const updateParam = (key, value) => {
    const params = new URLSearchParams(searchParams);

    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }

    // Reset page only when changing filters/search/sort
    if (key !== "page") {
      params.delete("page");
    }

    setSearchParams(params);
  };

  const handleAddToCart = (product) => {
    if (!user) return toast.error("Please log in to add items to your cart");
    addToCart(product.id, 1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <SEO
        title={search ? `Search: ${search}` : "Shop All Products"}
        description={search ? `Search results for "${search}" at FreshMart.` : "Browse the full FreshMart catalog — fruits, vegetables, dairy, snacks, and everyday essentials."}
        path="/products"
        noindex={!!search}
      />
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h1 className="text-xl font-semibold">
          {search ? `Results for "${search}"` : "All products"}
          <span className="text-sm text-gray-400 font-normal ml-2">{data.count} items</span>
        </h1>

        <label className="text-sm flex items-center gap-2">
          Sort by
          <select
            value={ordering}
            onChange={(e) => updateParam("ordering", e.target.value)}
            className="border border-gray-300 rounded-lg px-2 py-1"
          >
            <option value="">Relevance</option>
            <option value="discount_price">Price: Low to High</option>
            <option value="-discount_price">Price: High to Low</option>
            <option value="-rating_avg">Top Rated</option>
            <option value="-created_at">Newest</option>
          </select>
        </label>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="card h-64 animate-pulse bg-gray-100" />
          ))}
        </div>
      ) : data.results.length === 0 ? (
        <p className="text-center text-gray-500 py-16">No products found.</p>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {data.results.map((product) => (
              <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} />
            ))}
          </div>

          <nav aria-label="Pagination" className="flex justify-center gap-4 mt-8">
            <button
              disabled={!data.previous}
              onClick={() => updateParam("page", String(Number(page) - 1))}
              className="px-4 py-2 rounded-full border disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={!data.next}
              onClick={() => updateParam("page", String(Number(page) + 1))}
              className="px-4 py-2 rounded-full border disabled:opacity-40"
            >
              Next
            </button>
          </nav>
        </>
      )}
    </div>
  );
}
