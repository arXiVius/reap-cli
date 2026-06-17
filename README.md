# 🌾 reap

> A fast, beautiful, and modern CLI website archiver.

`reap` is an enhanced command-line wrapper built on top of `wget` and `wget2`. It simplifies downloading websites for offline viewing, offering faster multi-threaded performance, clean terminal visual reports, automatic asset routing for modern visual builders (such as Framer and Webflow), and built-in local hosting.

---

## ✨ Features

* **⚡ Autodetects `wget2`** — Automatically enables multi-threaded downloading (default: 8 parallel connections) for significantly faster downloads.
* **🎨 Visual Reports** — Beautiful status indicators, progress bars, and summary panels powered by `rich`.
* **🚀 Modern Builder Ready** — Automatically handles common CDN assets (Framer User Content, Google Fonts, etc.) to preserve site appearance offline.
* **🏃 Fast Mode (`--fast`)** — Skips large media files such as videos, archives, and audio to download layouts and styles quickly.
* **🌐 Instant Serve (`--serve`)** — Launches a lightweight local HTTP server for immediate offline previewing.
* **📦 Auto Archive (`--zip`)** — Automatically packages the downloaded site into a `.zip` archive.

---

## 📥 Installation

### Requirements

* Python 3.8+
* `wget` or `wget2` available in your system PATH

### Install from Source

```bash
git clone https://github.com/yourusername/reap.git
cd reap
pip install .
```

### Install Backend Engine

#### macOS

```bash
brew install wget2
```

#### Ubuntu / Debian

```bash
sudo apt install wget2
```

#### Windows

```powershell
winget install GNU.Wget
```

> `wget2` is recommended for maximum performance, but `wget` is also supported.

---

## 🚀 Usage

### Basic Website Download

Mirror a website into a directory named after its domain:

```bash
reap https://example.com
```

### Fast Layout Download

Skip videos, archives, and other heavy assets:

```bash
reap https://example.com --fast
```

### Download and Preview Locally

Mirror a site and immediately start a local server:

```bash
reap https://example.com --serve
```

The site will be available at:

```text
http://localhost:8000
```

### Increase Download Threads

Requires `wget2`.

```bash
reap https://example.com -t 16
```

### Automatically Create a ZIP Archive

```bash
reap https://example.com --zip
```

---

## 🧪 Development

Install in editable mode:

```bash
pip install -e .
```

After installation, the `reap` command will be available globally and will use your local source files. Any changes you make will be reflected immediately without reinstalling.

---

## 📄 License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2026 arxivius

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
