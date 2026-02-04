import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

/**
 * LEARNING NOTE:
 * Vite is a modern build tool that's much faster than Create React App.
 *
 * This config:
 * 1. Sets up React with fast refresh (hot module replacement)
 * 2. Configures PWA for mobile app-like experience
 * 3. Sets up path aliases (@ = src folder)
 *
 * TUTORIAL: https://vitejs.dev/config/
 */
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Sloth - Faultierdiät',
        short_name: 'Sloth',
        description: 'Dein Weg zum Wunschgewicht mit der Faultierdiät',
        theme_color: '#4F7942',  // Forest green - sloth vibes
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        // Cache API responses for offline use
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.sloth\.app\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      // This lets us import from '@/components/Button' instead of '../../../components/Button'
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    // Proxy API requests to backend during development
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
