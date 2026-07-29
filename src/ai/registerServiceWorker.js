/**
 * Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
 * Register Saphira PWA service worker.
 */

export function registerSaphiraServiceWorker() {
  if (typeof window === "undefined" || !("serviceWorker" in navigator)) {
    return;
  }

  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((reg) => {
        console.log("Saphira Service Worker active:", reg.scope);
      })
      .catch((err) => {
        console.error("Service Worker registration failed:", err);
      });
  });
}

// Auto-register when imported in browser bundles that execute side effects
if (typeof window !== "undefined") {
  registerSaphiraServiceWorker();
}
