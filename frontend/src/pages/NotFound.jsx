import { Link } from "react-router-dom";
import SEO from "../components/SEO.jsx";

export default function NotFound() {
  return (
    <div className="max-w-md mx-auto px-4 py-24 text-center">
      <SEO title="Page Not Found" description="The page you're looking for doesn't exist." path="/404" noindex />
      <h1 className="text-4xl font-bold text-primary mb-2">404</h1>
      <p className="text-gray-500 mb-6">Page not found.</p>
      <Link to="/" className="btn-primary">Back to home</Link>
    </div>
  );
}
