import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    allowedHosts: true,
    cors: true,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/map-tiles": {
        target: "https://server.arcgisonline.com",
        changeOrigin: true,
        rewrite: (path) =>
          path.replace(/^\/map-tiles/, "/ArcGIS/rest/services/World_Street_Map/MapServer/tile"),
      },
    },
  },
})
