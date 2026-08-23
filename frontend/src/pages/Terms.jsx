import SEO from "../components/SEO.jsx";

export default function Terms() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <SEO
        title="Terms of Service"
        description="The terms and conditions for using FreshMart."
        path="/terms"
      />
      <h1 className="text-2xl font-bold mb-4">Terms of Service</h1>
      <p className="text-gray-600 dark:text-gray-300">
        By using FreshMart, you agree to place orders in good faith and provide accurate
        delivery information. Prices and availability are subject to change.
      </p>
    </div>
  );
}
