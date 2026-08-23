import { motion } from "framer-motion";

/**
 * Full-screen branded loading state — used as the Suspense fallback while
 * route chunks load, and can be reused anywhere else a full-page loader
 * is needed (e.g. auth bootstrapping).
 */
export default function LoadingPage({ label = "Loading FreshMart..." }) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={label}
      className="min-h-[70vh] w-full flex flex-col items-center justify-center gap-6 bg-bg dark:bg-gray-950"
    >
      <div className="relative w-20 h-20">
        <motion.span
          className="absolute inset-0 rounded-full border-4 border-primary/20"
          aria-hidden="true"
        />
        <motion.span
          className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 0.9, ease: "linear" }}
          aria-hidden="true"
        />
        <motion.div
          className="absolute inset-0 flex items-center justify-center text-2xl"
          animate={{ scale: [1, 1.12, 1] }}
          transition={{ repeat: Infinity, duration: 1.4, ease: "easeInOut" }}
          aria-hidden="true"
        >
          🥬
        </motion.div>
      </div>

      <div className="text-center">
        <p className="text-lg font-bold text-primary">FreshMart</p>
        <p className="text-sm text-gray-400 mt-1">{label}</p>
      </div>

      <div className="flex gap-1.5" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-primary"
            animate={{ opacity: [0.25, 1, 0.25] }}
            transition={{ repeat: Infinity, duration: 1, delay: i * 0.15 }}
          />
        ))}
      </div>
    </div>
  );
}
