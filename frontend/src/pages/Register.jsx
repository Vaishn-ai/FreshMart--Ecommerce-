import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext.jsx";
import SEO from "../components/SEO.jsx";

export default function Register() {
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm();
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      await registerUser(data);
      toast.success("Account created!");
      navigate("/");
    } catch (err) {
      const detail = err.response?.data;
      toast.error(typeof detail === "object" ? Object.values(detail)[0]?.[0] || "Registration failed" : "Registration failed");
    }
  };

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <SEO title="Create Account" path="/register" noindex />
      <h1 className="text-2xl font-bold mb-6 text-center">Create your account</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div>
          <label htmlFor="username" className="block text-sm mb-1">Username</label>
          <input id="username" className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("username", { required: "Username is required" })} />
          {errors.username && <p role="alert" className="text-red-500 text-xs mt-1">{errors.username.message}</p>}
        </div>
        <div>
          <label htmlFor="email" className="block text-sm mb-1">Email</label>
          <input id="email" type="email" className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("email", { required: "Email is required" })} />
          {errors.email && <p role="alert" className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
        </div>
        <div>
          <label htmlFor="phone" className="block text-sm mb-1">Phone</label>
          <input id="phone" className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("phone")} />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm mb-1">Password</label>
          <input id="password" type="password" className="w-full rounded-xl border border-gray-300 px-3 py-2" {...register("password", { required: "Password is required", minLength: { value: 8, message: "At least 8 characters" } })} />
          {errors.password && <p role="alert" className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
        </div>
        <div>
          <label htmlFor="password2" className="block text-sm mb-1">Confirm password</label>
          <input
            id="password2"
            type="password"
            className="w-full rounded-xl border border-gray-300 px-3 py-2"
            {...register("password2", {
              required: "Please confirm your password",
              validate: (val) => val === watch("password") || "Passwords do not match",
            })}
          />
          {errors.password2 && <p role="alert" className="text-red-500 text-xs mt-1">{errors.password2.message}</p>}
        </div>

        <button type="submit" disabled={isSubmitting} className="btn-primary w-full disabled:opacity-60">
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p className="text-sm text-center mt-6">
        Already have an account? <Link to="/login" className="text-primary font-medium">Log in</Link>
      </p>
    </div>
  );
}
