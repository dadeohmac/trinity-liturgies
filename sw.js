// Trinity Liturgies service worker. Caches nothing: every request goes to the
// network as usual. It only exists so browsers treat the site as installable,
// and to show a friendly page instead of a browser error when offline.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", e => {
  if (e.request.mode !== "navigate") return; // videos, JSON, icons: untouched
  e.respondWith(fetch(e.request).catch(() => new Response(
    '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>Trinity Liturgies</title><body style="font:17px/1.5 -apple-system,system-ui,sans-serif;padding:40px 20px;text-align:center;background:#1d2533;color:#e7eaef">' +
    '<h1 style="font-weight:400">You\'re offline</h1><p>Trinity Liturgies needs an internet connection to load services. Reconnect and try again.</p>' +
    '<p><button onclick="location.reload()" style="font:inherit;padding:10px 20px;border-radius:10px;border:0">Try again</button></p>',
    { headers: { "Content-Type": "text/html; charset=utf-8" } })));
});
