import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import App from "./App.jsx";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import { CartProvider } from "./contexts/CartContext.jsx";
import { Toaster } from "react-hot-toast";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <HelmetProvider>
      <BrowserRouter future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
    }}
>
        <AuthProvider>
          <CartProvider>
            <Toaster position="top-center" />
            
            <App />
          </CartProvider>
        </AuthProvider>
      </BrowserRouter>
    </HelmetProvider>
  </React.StrictMode>
);

// Fade out and remove the static HTML splash screen (index.html) now that
// React has taken over rendering.
const initialLoader = document.getElementById("initial-loader");
if (initialLoader) {
  initialLoader.classList.add("fade-out");
  setTimeout(() => initialLoader.remove(), 300);
}
