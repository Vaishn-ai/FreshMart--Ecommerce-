import SEO from "../components/SEO.jsx";

const faqs = [
  { q: "What are your delivery hours?", a: "We deliver daily from 7am to 10pm." },
  { q: "What payment methods do you accept?", a: "Cash on Delivery, Razorpay, Stripe, and UPI." },
  { q: "Can I return a product?", a: "Yes — perishables within 24 hours, non-perishables within 7 days." },
];

const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: faqs.map((f) => ({
    "@type": "Question",
    name: f.q,
    acceptedAnswer: { "@type": "Answer", text: f.a },
  })),
};

export default function FAQ() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <SEO
        title="FAQ"
        description="Answers to common questions about delivery, payments, and returns at FreshMart."
        path="/faq"
        jsonLd={faqJsonLd}
      />
      <h1 className="text-2xl font-bold mb-6">Frequently Asked Questions</h1>
      <dl className="space-y-6">
        {faqs.map((f) => (
          <div key={f.q}>
            <dt className="font-semibold">{f.q}</dt>
            <dd className="text-gray-600 dark:text-gray-300 mt-1">{f.a}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
