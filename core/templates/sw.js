// Service Worker - Application UJK (Union des Jeunes de Kakony)
// Stratégie : network-first avec repli sur le cache (adapté aux données dynamiques)

const CACHE_NAME = "ujk-cache-v1"; // incrémenter (v2, v3...) à chaque déploiement majeur
const OFFLINE_URL = "/offline/";

const PRECACHE_URLS = [
  "/",
  OFFLINE_URL,
  "/static/manifest.json",
  "/static/css/dist/styles.css", // ajuste selon le chemin généré par django-tailwind
  "/static/logo.png",
  "/static/logo.png",
];

// Installation : mise en cache des ressources essentielles
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS).catch((err) => {
        // Ne bloque pas l'installation si une ressource précise échoue
        console.warn("Pré-cache partiel :", err);
      });
    })
  );
  self.skipWaiting();
});

// Activation : nettoyage des anciens caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Interception des requêtes
self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Ne jamais intercepter les requêtes non-GET (formulaires, paiements, cotisations, etc.)
  if (request.method !== "GET") {
    return;
  }

  // Ne pas mettre en cache les appels API/admin sensibles si besoin (ajuster selon les routes)
  const url = new URL(request.url);
  if (url.pathname.startsWith("/admin/")) {
    return;
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        // Copie la réponse pour la mettre en cache (une réponse ne se lit qu'une fois)
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseClone);
        });
        return response;
      })
      .catch(() => {
        // Hors ligne : on sert le cache, sinon la page offline
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // Si c'est une navigation de page HTML, afficher la page offline
          if (request.mode === "navigate") {
            return caches.match(OFFLINE_URL);
          }
          return new Response("", { status: 504, statusText: "Hors ligne" });
        });
      })
  );
});