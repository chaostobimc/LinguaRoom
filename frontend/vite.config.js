import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// In development the React dev server proxies API + WebSocket traffic to the
// Python backend running on :8000. In production the backend serves the built
// files from frontend/dist, so no proxy is needed.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
});
