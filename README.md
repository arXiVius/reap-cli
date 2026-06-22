# 🌾 reap v2

> A deterministic web reconstruction and deployment engine.

`reap` is a modern CLI tool built purely in Python that intelligently crawls websites, resolves and extracts all modern web assets (including SPA assets and CDNs like Framer/Webflow), rewrites the broken web structure for local navigation, and even emulates modern SPA behavior. Downloaded sites behave exactly like they are still online.

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
git clone https://github.com/arXiVius/reap-cli.git
cd reap-cli
pip install .
```

*Note: For maximum stability, it is recommended to install `reap-cli` in an isolated virtual environment (like `venv` or `pipx`) to prevent dependency conflicts with system packages.*

### Optional Dependencies

```bash
# Image optimization (WebP conversion)
pip install 'reap-cli[optimize]'

# JS snapshot mode (headless browser rendering)
pip install 'reap-cli[pdf]'
playwright install
```

---

## 🧭 Recommended Usage Path

Because `reap` has many flags, here is the recommended setup depending on your goal:

* **Basic offline mirror**: `reap https://example.com --mode mirror`
* **Modern React/Vue/SPA sites**: `reap https://example.com --mode app --js`
* **Fast lightweight capture**: `reap https://example.com --fast`

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

```bash
reap https://example.com --mode app --js
```

### Download and Preview Locally

```bash
reap https://example.com --serve
```

### Identity & Credits

```bash
reap --version        # Version with author credit
reap --about          # Full project info panel
reap --help           # Structured help with identity header
```

---

## 🏗️ CLI Structure

```
reap <url>                # main tool
reap --help               # structured, light identity
reap --version            # full credit
reap --about              # full project info
```

---

## 📄 License

MIT License

---

## ⚠️ Known Limitations & Risks

Please review the [LIMITATIONS.md](LIMITATIONS.md) file for a detailed risk map regarding JavaScript-generated content, SPA routing edge cases, dynamic APIs, and offline behavior mismatches.
