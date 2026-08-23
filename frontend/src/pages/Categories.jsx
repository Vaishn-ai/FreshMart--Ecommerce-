import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import SEO from "../components/SEO";

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const { data } = await api.get("/categories/");
        setCategories(data.results || data);
      } catch (error) {
        console.error("Failed to load categories:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  const handleCategoryClick = (category) => {
    navigate(`/products?category=${category.slug}`);
  };

  if (loading) {
    return (
      <>
        <SEO title="Categories" path="/categories" />
        <div className="max-w-6xl mx-auto px-4 py-16 text-center">
          Loading categories...
        </div>
      </>
    );
  }

  return (
    <>
      <SEO title="Categories" path="/categories" />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Shop by Category</h1>

        {categories.length === 0 ? (
          <p className="text-center text-gray-500">
            No categories available.
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategoryClick(category)}
                className="card p-5 rounded-xl hover:shadow-xl hover:-translate-y-1 transition-all duration-300 text-center"
              >
                {category.image ? (
                  <img
                    src={category.image}
                    alt={category.name}
                    className="w-24 h-24 mx-auto rounded-full object-cover border mb-4"
                  />
                ) : (
                  <div className="w-24 h-24 mx-auto rounded-full bg-gray-100 flex items-center justify-center mb-4 text-3xl">
                    🛒
                  </div>
                )}

                <h2 className="font-semibold text-lg">
                  {category.name}
                </h2>
              </button>
            ))}
          </div>
        )}
      </div>
    </>
  );
}