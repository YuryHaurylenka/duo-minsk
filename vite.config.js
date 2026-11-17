import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';
export default defineConfig({
  root: 'frontend',
  plugins: [react()],
  build: { outDir: resolve(process.cwd(), 'public'), emptyOutDir: false, assetsDir: 'assets', rollupOptions: { output: { manualChunks: { charts: ['recharts'], motion: ['framer-motion'], supabase: ['@supabase/supabase-js'], icons: ['lucide-react'] } } } },
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } }
});
