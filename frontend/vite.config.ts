import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // En desarrollo: `docker compose up` deja la API detrás de nginx en :8080
    proxy: { "/api": process.env.API_URL ?? "http://localhost:8080" },
  },
});
