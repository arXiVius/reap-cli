# 🌾 reap v2

> A fast, beautiful, and modern offline web reconstruction engine.

`reap` v2 is an advanced CLI tool built purely in Python that completely replaces wget wrappers. It's an offline web reconstruction system that intelligently crawls websites, resolves and extracts all modern web assets (including SPA assets and CDNs like Framer/Webflow), rewrites the broken web structure for local navigation, and even emulates modern SPA behavior. Downloaded sites behave exactly like they are still online.

---

## ✨ Features

* **🧠 Smart Native Graph Engine** — Asynchronous, native Python graph crawling with deep DOM parsing instead of blind downloads.
* **🚀 SPA & Modern Framework Handler** — Generates `index.html` router fallbacks and properly routes navigation for React/Next.js/Vue apps.
* **🧩 Deep Asset Extraction** — Grabs assets not just from `src` and `href`, but parses `srcset`, `data-src`, `data-bg`, and even parses CSS for `url(...)` resources.
* **🔗 Link Rewrite Engine** — Re-maps all URLs to relative local paths, completely fixing broken navigation for offline viewing.
* **🧹 Smart Cleanup Layer** — Automatically filters and strips out analytics scripts, tracking pixels, ad networks, and cookie overlays.
* **🏃 Adaptive Downloader** — Uses `aiohttp` for streaming, fast, concurrent downloading without heavy disk I/O spikes.
* **🧪 JS Snapshot Mode (Optional)** — Utilizes headless Playwright to snapshot dynamically rendered JavaScript dashboards before scraping.

## 🧭 Mode System
* `--mode mirror` - Exact replica (full fidelity)
* `--mode app` - SPA-aware reconstruction (recommended, default)
* `--mode reader` - Clean article extraction (removes nav, footer, scripts)
* `--mode fast` - Layout-only minimal download, skipping heavy media

---

## 📥 Installation

### Requirements

* Python 3.8+

### Install from Source

```bash
git clone https://github.com/yourusername/reap.git
cd reap
pip install .
```

---

## 🚀 Usage

### Basic SPA Reconstruction

```bash
reap https://example.com --mode app
```

### Clean Reader Mode Extraction

```bash
reap https://example.com --mode reader
```

### Pure Layout Minimal Extraction

```bash
reap https://example.com --mode fast
```

### Full Interactive JS Snapshot Pipeline

Requires Playwright installed: `pip install playwright && playwright install`

```bash
reap https://example.com --mode app --js
```

### Download and Preview Locally

```bash
reap https://example.com --serve
```

---

## 📄 License

MIT License

---

## ⚠️ Known Limitations & Risks
Please review the [LIMITATIONS.md](LIMITATIONS.md) file for a detailed risk map regarding JavaScript-generated content, SPA routing edge cases, dynamic APIs, and offline behavior mismatches.
