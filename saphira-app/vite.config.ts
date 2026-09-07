import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import fs from 'fs';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const apiUrl = (env.SAPHIRA_API_URL || env.VITE_SAPHIRA_API_BASE_URL || '/api').replace(/\/$/, '');

  // Preserve the existing 192/512 PWA icon assets while the legacy root
  // static surface is retired. They are copied into the canonical Vite
  // public directory at build time and are never served as application UI.
  const legacyIcons = path.resolve(__dirname, '../public/icons');
  const appIcons = path.resolve(__dirname, './public/icons');
  if (fs.existsSync(legacyIcons)) {
    fs.mkdirSync(appIcons, { recursive: true });
    fs.cpSync(legacyIcons, appIcons, { recursive: true });
  }

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    define: {
      'import.meta.env.VITE_SAPHIRA_API_BASE_URL': JSON.stringify(apiUrl),
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  };
});
