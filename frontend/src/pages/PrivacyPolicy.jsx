import SEO from "../components/SEO.jsx";

export default function PrivacyPolicy() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <SEO
        title="Privacy Policy"
        description="How FreshMart collects, uses, and protects your personal information."
        path="/privacy-policy"
      />
      <h1 className="text-2xl font-bold mb-4">Privacy Policy</h1>
      <p className="text-gray-600 dark:text-gray-300">
        FreshMart collects only the information needed to process your orders and improve
        your shopping experience. We never sell your personal data to third parties.
      </p>
    </div>
  );
}
