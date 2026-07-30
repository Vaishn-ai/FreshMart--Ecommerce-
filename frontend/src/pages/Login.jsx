import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext.jsx";
import SEO from "../components/SEO.jsx";

export default function Login() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();
  const { login } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      await login(data.email, data.password);
      toast.success("Welcome back!");
      navigate("/");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Invalid email or password");
    }
  };

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <SEO title="Log In" path="/login" noindex />
      <h1 className="text-2xl font-bold mb-6 text-center">Log in to FreshMart</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div>
          <label htmlFor="email" className="block text-sm mb-1">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            className="w-full rounded-xl border border-gray-300 px-3 py-2"
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "email-error" : undefined}
            {...register("email", { required: "Email is required" })}
          />
          {errors.email && <p id="email-error" role="alert" className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm mb-1">Password</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            className="w-full rounded-xl border border-gray-300 px-3 py-2"
            aria-invalid={!!errors.password}
            {...register("password", { required: "Password is required" })}
          />
          {errors.password && <p role="alert" className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
        </div>

        <Link to="/forgot-password" className="text-sm text-primary block text-right">Forgot password?</Link>

        <button type="submit" disabled={isSubmitting} className="btn-primary w-full disabled:opacity-60">
          {isSubmitting ? "Logging in..." : "Log in"}
        </button>
      </form>
      <p className="text-sm text-center mt-6">
        New here? <Link to="/register" className="text-primary font-medium">Create an account</Link>
      </p>
    </div>
  );
}
