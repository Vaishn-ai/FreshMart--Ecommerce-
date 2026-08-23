import { useForm } from "react-hook-form";
import { useState } from "react";
import api from "../services/api";
import SEO from "../components/SEO.jsx";

export default function ForgotPassword() {
  const { register, handleSubmit, formState: { isSubmitting } } = useForm();
  const [sent, setSent] = useState(false);

  const onSubmit = async (data) => {
    await api.post("/auth/forgot-password/", data);
    setSent(true);
  };

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <SEO title="Reset Password" path="/forgot-password" noindex />
      <h1 className="text-2xl font-bold mb-6 text-center">Reset your password</h1>
      {sent ? (
        <p role="status" className="text-center text-gray-600">
          If that email is registered, we've sent a reset link — check your inbox.
        </p>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <label htmlFor="email" className="block text-sm mb-1">Email</label>
            <input id="email" type="email" required className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("email", { required: true })} />
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full disabled:opacity-60">
            {isSubmitting ? "Sending..." : "Send reset link"}
          </button>
        </form>
      )}
    </div>
  );
}
