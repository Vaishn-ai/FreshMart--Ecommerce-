import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { MdOutlineShoppingCart, MdOutlineFavoriteBorder, MdOutlinePerson, MdMenu, MdClose, MdSearch } from "react-icons/md";
import { useAuth } from "../contexts/AuthContext.jsx";
import { useCart } from "../contexts/CartContext.jsx";
import BrandStrip from "../components/BrandStrip";

export default function MainLayout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();
  const itemCount = cart?.items?.reduce((sum, i) => sum + i.quantity, 0) || 0;

  const handleSearch = (e) => {
    e.preventDefault();
    const q = e.target.elements.q.value.trim();
    if (q) navigate(`/products?search=${encodeURIComponent(q)}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-bg dark:bg-gray-950">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-primary text-white px-3 py-2 rounded z-50">
        Skip to content
      </a>

      <header className="sticky top-0 z-40 bg-white/90 dark:bg-gray-900/90 backdrop-blur border-b border-gray-100 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-4">
          <button
            className="md:hidden p-2"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((o) => !o)}
          >
            {menuOpen ? <MdClose size={22} /> : <MdMenu size={22} />}
          </button>

          <Link to="/" className="text-xl font-bold text-primary shrink-0">
            FreshMart
          </Link>

          <form onSubmit={handleSearch} role="search" className="hidden md:flex flex-1 max-w-md">
            <label htmlFor="nav-search" className="sr-only">Search products</label>
            <div className="flex items-center w-full bg-gray-100 dark:bg-gray-800 rounded-full px-4 py-2">
              <MdSearch className="text-gray-400 mr-2" aria-hidden="true" />
              <input id="nav-search" name="q" type="search" placeholder="Search groceries..." className="bg-transparent outline-none w-full text-sm" />
            </div>
          </form>

          <nav aria-label="Primary" className="ml-auto flex items-center gap-4">
            {user?.is_superuser && (
              <Link to="/manage-products" aria-label="Manage products" className="text-xs font-semibold text-primary hover:underline hidden md:inline">
                Manage Products
              </Link>
            )}
            <Link to="/wishlist" aria-label="Wishlist" className="p-2 hover:text-primary transition-colors">
              <MdOutlineFavoriteBorder size={22} />
            </Link>
            <Link to="/cart" aria-label={`Cart, ${itemCount} items`} className="relative p-2 hover:text-primary transition-colors">
              <MdOutlineShoppingCart size={22} />
              {itemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-accent text-gray-900 text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
                  {itemCount}
                </span>
              )}
            </Link>
            {user ? (
              <div className="flex items-center gap-2">
                <Link to="/profile" aria-label="My profile" className="p-2 hover:text-primary transition-colors">
                  <MdOutlinePerson size={22} />
                </Link>
                <button onClick={logout} className="text-sm text-gray-500 hover:text-primary hidden sm:inline">
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn-primary !px-4 !py-2 text-sm">Login</Link>
            )}
          </nav>
        </div>

        {menuOpen && (
          <nav aria-label="Mobile" className="md:hidden border-t border-gray-100 dark:border-gray-800 px-4 py-3 flex flex-col gap-3">
            <Link to="/products" onClick={() => setMenuOpen(false)}>Products</Link>
            <Link to="/categories" onClick={() => setMenuOpen(false)}>Categories</Link>
            <Link to="/orders" onClick={() => setMenuOpen(false)}>My Orders</Link>
            {user?.is_superuser && <Link to="/manage-products" onClick={() => setMenuOpen(false)} className="text-primary font-semibold">Manage Products</Link>}
            <Link to="/about" onClick={() => setMenuOpen(false)}>About</Link>
            <Link to="/contact" onClick={() => setMenuOpen(false)}>Contact</Link>
          </nav>
        )}
      </header>

      <BrandStrip />

      <main id="main-content" className="flex-1">
        {children}
      </main>

      <footer className="bg-gray-900 text-gray-300 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-2 md:grid-cols-4 gap-8 text-sm">
          <div>
            <h2 className="text-white font-semibold mb-3">FreshMart</h2>
            <p>Fresh groceries, delivered fast.</p>
          </div>
          <nav aria-label="Company">
            <h3 className="text-white font-semibold mb-3">Company</h3>
            <ul className="space-y-2">
              <li><Link to="/about">About</Link></li>
              <li><Link to="/contact">Contact</Link></li>
              <li><Link to="/faq">FAQ</Link></li>
            </ul>
          </nav>
          <nav aria-label="Legal">
            <h3 className="text-white font-semibold mb-3">Legal</h3>
            <ul className="space-y-2">
              <li><Link to="/privacy-policy">Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Service</Link></li>
            </ul>
          </nav>
          <div>
            <h3 className="text-white font-semibold mb-3">Get the app</h3>
            <p>Download FreshMart for faster checkout and exclusive deals.</p>
          </div>
        </div>
        <div className="text-center text-xs text-gray-500 pb-6">© {new Date().getFullYear()} FreshMart. All rights reserved.</div>
      </footer>
    </div>
  );
}
