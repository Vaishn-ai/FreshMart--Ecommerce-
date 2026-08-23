import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function BrandStrip() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBrands();
  }, []);

  const fetchBrands = async () => {
    try {
      const { data } = await api.get("/brands/");

      console.log("Brands:", data);

      const brandList = Array.isArray(data)
        ? data
        : data.results || [];

      setBrands(brandList);
    } catch (error) {
      console.error("Unable to load brands", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || brands.length === 0) return null;

  return (
    <section className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-3">

        <div className="flex gap-5 overflow-x-auto scrollbar-hide">

          {brands.map((brand) => (

            <Link
              key={brand.id}
              to={`/products?brand=${brand.slug}`}
              className="flex flex-col items-center shrink-0 group"
            >

              <div className="w-16 h-16 rounded-full bg-white shadow border flex items-center justify-center overflow-hidden">

                <img
                  src={brand.logo}
                  alt={brand.name}
                  className="w-12 h-12 object-contain transition duration-300 group-hover:scale-110"
                />

              </div>

              <span className="text-xs mt-2 font-medium">
                {brand.name}
              </span>

            </Link>

          ))}

        </div>

      </div>
    </section>
  );
}