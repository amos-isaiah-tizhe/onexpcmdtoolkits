# OneXportal Toolkit — PWA Upgrade

Make your Netlify site installable on phones and fully usable offline.

## 1. Files to add (drop into your repo)

Place these at the indicated paths inside your project root
(`onexpcmdtoolkits/`), then commit and push to Netlify:

```
onexpcmdtoolkits/
├── manifest.webmanifest        ← NEW (root)
├── sw.js                       ← NEW (root — MUST be at root for scope "/")
├── offline.html                ← NEW (root)
└── img/
    ├── icon-192.png            ← NEW
    ├── icon-512.png            ← NEW
    └── apple-touch-icon.png    ← NEW
```

> `sw.js` must live at the **site root** so its scope covers the whole app.
> Don't put it inside `/assets/`.

## 2. Edit your 3 HTML pages

Open each of:

- `index.html`
- `termux-ops.html`
- `git-termux.html`

### 2a. Add inside `<head>` (after the existing favicon links):

```html
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#0d1117">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="OneXp Toolkit">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
```

### 2b. Add right before `</body>`:

```html
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function (err) {
        console.warn('SW registration failed:', err);
      });
    });
  }
</script>
```

(Both snippets are also in `HEAD-SNIPPET.html` for copy-paste.)

## 3. Deploy to Netlify

Commit + push, or drag-and-drop the folder into Netlify. No build
config changes needed — Netlify serves the files as-is over HTTPS,
which is the only requirement for a service worker to run.

## 4. Test it works

1. Open your site on Chrome (desktop): DevTools → Application → Manifest.
   You should see the icon + "Installable".
2. DevTools → Application → Service Workers — `sw.js` should be
   `activated and running`.
3. Toggle DevTools → Network → "Offline", reload — the site still loads.

## 5. How users install it on their phone

**Android (Chrome):** Visit the site → tap the ⋮ menu → **Install app**
(or "Add to Home screen"). It launches fullscreen with your icon.

**iPhone (Safari):** Visit the site → tap the Share button →
**Add to Home Screen**.

After install, opening the app icon works with **no internet** — every
page they've visited at least once stays cached.

## 6. Updating later

When you change your HTML/CSS/JS, bump the version string at the top of
`sw.js`:

```js
const VERSION = 'v1.0.1';
```

Users get the new version automatically on their next visit.

## Notes

- The service worker precaches all 3 HTML pages and both JSON command
  files, so the toolkit is fully usable offline immediately after the
  first visit.
- Font Awesome and Google Fonts are loaded from CDN — they're cached
  on first use via stale-while-revalidate, so they also work offline
  after one online visit.
- If you ever want to remove the PWA, delete `sw.js` and replace it
  with an empty kill-switch worker that calls
  `self.registration.unregister()` so installed users get cleaned up.
