import SEO from "../components/SEO.jsx";

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 prose dark:prose-invert">
      <SEO
        title="About Us"
        description="Learn about FreshMart — delivering fresh groceries and everyday essentials right to your door, at honest prices."
        path="/about"
      />
      <h1 className="text-2xl font-bold mb-4">About FreshMart</h1>
      <p className="text-gray-600 dark:text-gray-300">
        FreshMart delivers fresh groceries and everyday essentials right to your door,
        at honest prices, with same-day delivery in select areas.
      </p>
    </div>
  );
}
