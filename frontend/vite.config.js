import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
    build: {
      manifest: "manifest.json",
    outDir: '../passwordmanager/frontend/static/build', // output assest into the django app static files
    emptyOutDir: true                      // deletes old stuff before adding built files
  }
})
