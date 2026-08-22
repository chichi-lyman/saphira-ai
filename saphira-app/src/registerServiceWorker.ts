/**
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Canonical Saphira PWA service-worker registration.
 */

export function registerServiceWorker(): void {
  if (!('serviceWorker' in navigator)) return;

  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then((registration) => {
        console.info('Saphira PWA service worker registered:', registration.scope);
      })
      .catch((error) => {
        console.error('Saphira PWA service worker registration failed:', error);
      });
  }, { once: true });
}
