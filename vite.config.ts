import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 8501,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:11434",
        changeOrigin: true,
      },
    },
  },
});
