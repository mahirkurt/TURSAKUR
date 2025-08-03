import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App.jsx'
import { supabase } from './lib/supabase.js'

// Material Design 3 Tüm Stil Dosyaları
import './styles/index.css'
// Override CSS for elliptical elements fix
import './styles/override.css'

// TanStack Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 dakika
      cacheTime: 10 * 60 * 1000, // 10 dakika
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Global erişim için (debugging amaçlı)
window.supabase = supabase
window.queryClient = queryClient

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>,
)
