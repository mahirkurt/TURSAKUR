import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(fileURLToPath(new URL('./src', import.meta.url))),
      '@components': resolve(fileURLToPath(new URL('./src/components', import.meta.url))),
      '@pages': resolve(fileURLToPath(new URL('./src/pages', import.meta.url))),
      '@styles': resolve(fileURLToPath(new URL('./src/styles', import.meta.url))),
      '@utils': resolve(fileURLToPath(new URL('./src/utils', import.meta.url))),
      '@hooks': resolve(fileURLToPath(new URL('./src/hooks', import.meta.url))),
      '@contexts': resolve(fileURLToPath(new URL('./src/contexts', import.meta.url))),
    },
  },
  server: {
    port: 3000,
    open: true,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
          supabase: ['@supabase/supabase-js'],
          maps: ['leaflet', 'react-leaflet'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@supabase/supabase-js'],
  },
})
