import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: "../src/rigbook/static",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://localhost:8073",
    },
  },
});
