import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { MdOutlineShoppingCart, MdFavoriteBorder, MdStar } from "react-icons/md";

export default function ProductCard({ product, onAddToCart, onToggleWishlist }) {
  const { id, name, unit, weight_or_size, mrp, discount_price, discount_percent, rating_avg, primary_image, in_stock } = product;

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className="card relative flex flex-col overflow-hidden p-3 w-full max-w-[220px]"
    >
      {discount_percent > 0 && (
        <span className="absolute top-3 left-3 z-10 bg-accent text-gray-900 text-xs font-semibold px-2 py-1 rounded-full">
          {discount_percent}% OFF
        </span>
      )}

      <button
        onClick={() => onToggleWishlist?.(product)}
        className="absolute top-3 right-3 z-10 bg-white/80 backdrop-blur rounded-full p-1.5 hover:bg-white transition-colors"
        aria-label="Add to wishlist"
      >
        <MdFavoriteBorder className="text-gray-700" size={18} />
      </button>

      <div className="aspect-square rounded-2xl bg-gray-50 overflow-hidden mb-3">
        <Link to={`/products/${id}`} aria-label={`View ${name}`}>
          {primary_image ? (
            <img src={primary_image} alt={name} className="w-full h-full object-cover" loading="lazy" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300 text-xs">No image</div>
          )}
        </Link>
      </div>

      <Link to={`/products/${id}`}>
        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">{name}</h3>
      </Link>
      <p className="text-xs text-gray-500 mb-1">{weight_or_size || unit}</p>

      <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
        <MdStar className="text-accent" size={14} />
        <span>{Number(rating_avg).toFixed(1)}</span>
      </div>

      <div className="flex items-center justify-between mt-auto">
        <div>
          <span className="font-semibold text-gray-900 dark:text-white">₹{discount_price}</span>
          {mrp > discount_price && <span className="text-xs text-gray-400 line-through ml-1">₹{mrp}</span>}
        </div>
        <button
          disabled={!in_stock}
          onClick={() => onAddToCart?.(product)}
          className="btn-primary !px-3 !py-2 disabled:opacity-40 disabled:pointer-events-none"
          aria-label="Add to cart"
        >
          <MdOutlineShoppingCart size={16} />
        </button>
      </div>

      {!in_stock && <p className="text-xs text-red-500 mt-1">Out of stock</p>}
    </motion.div>
  );
}
