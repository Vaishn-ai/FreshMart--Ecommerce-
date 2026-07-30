import { useForm } from "react-hook-form";
import { useState } from "react";
import SEO from "../components/SEO.jsx";

export default function Contact() {
  const { register, handleSubmit, reset } = useForm();
  const [sent, setSent] = useState(false);

  const onSubmit = () => {
    setSent(true);
    reset();
  };

  return (
    <div className="max-w-md mx-auto px-4 py-12">
      <SEO title="Contact Us" description="Get in touch with the FreshMart team." path="/contact" />
      <h1 className="text-2xl font-bold mb-6">Contact us</h1>
      {sent && <p role="status" className="text-primary mb-4">Thanks — we'll get back to you shortly.</p>}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm mb-1">Name</label>
          <input id="name" required className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("name")} />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm mb-1">Email</label>
          <input id="email" type="email" required className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("email")} />
        </div>
        <div>
          <label htmlFor="message" className="block text-sm mb-1">Message</label>
          <textarea id="message" required rows={4} className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("message")} />
        </div>
        <button type="submit" className="btn-primary w-full">Send message</button>
      </form>
    </div>
  );
}
