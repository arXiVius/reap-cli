import asyncio
import aiohttp
import os
import posixpath
import re
import hashlib
import json
import shutil
import time
import mimetypes
import tempfile
from urllib.parse import urlparse, urljoin, unquote, urlunparse, parse_qs, urlencode
from bs4 import BeautifulSoup
from reap import __version__
from reap.utils import print_msg

try:
    from rich.console import Console
    from rich.panel import Panel
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEAVY_EXTENSIONS = {".mp4", ".mp3", ".wav", ".avi", ".mkv", ".zip", ".tar", ".gz", ".rar", ".pdf", ".dmg", ".exe", ".apk", ".iso"}

CSS_URL_PATTERN = re.compile(r'url\((?:["\']?)(.*?)(?:["\']?)\)')
TRACKER_KEYWORDS = ['analytics', 'tracking', 'pixel', 'adsystem', 'gtag', 'fbq', 'google-analytics', 'mixpanel']

def normalize_url(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    for k in list(qs.keys()):
        if k.lower() in ('v', 'cache') or k.lower().startswith('utm_'):
            del qs[k]
    netloc = re.sub(r'^cdn\d+\.', 'cdn.', parsed.netloc)
    new_query = urlencode(qs, doseq=True)
    parsed = parsed._replace(netloc=netloc, query=new_query, fragment='')
    return urlunparse(parsed)

def is_same_domain(url, base_netloc):
    parsed = urlparse(url)
    if not parsed.netloc: return True
    return parsed.netloc == base_netloc or parsed.netloc.endswith("." + base_netloc)

def get_page_local_path(url, base_dir, mode="app"):
    parsed = urlparse(url)
    path = unquote(parsed.path)
    if not path or path == "/": path = "/index.html"
    elif path.endswith("/"): path += "index.html"
    elif not path.endswith(".html") and mode == "app": path += "/index.html"
    elif not path.endswith(".html"): path += ".html"
        
    path = path.lstrip("/")
    return os.path.join(base_dir, path.replace("/", os.sep)), f"/{path}"

def get_relative_url(from_url_path, to_url_path):
    from_dir = posixpath.dirname(from_url_path)
    return posixpath.relpath(to_url_path, from_dir)

def get_priority(url, is_page=False):
    if is_page: return 1
    lower = url.lower()
    if lower.endswith('.css'): return 2
    if lower.endswith('.js'): return 3
    if any(lower.endswith(ext) for ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.woff', '.woff2', '.ttf'}):
        return 4
    return 5

class DynamicLimit:
    def __init__(self, limit=5):
        self.limit = limit
        self.current = 0
        self.cond = asyncio.Condition()
        self.ema_latency = 0.5
        self.alpha = 0.2 # Damping factor
        
    async def acquire(self):
        async with self.cond:
            await self.cond.wait_for(lambda: self.current < self.limit)
            self.current += 1
            
    async def release(self):
        async with self.cond:
            self.current -= 1
            self.cond.notify()
            
    async def update_latency(self, latency, is_429=False, base_threads=8):
        async with self.cond:
            if is_429:
                self.limit = max(1, self.limit // 2)
            else:
                self.ema_latency = (self.alpha * latency) + ((1 - self.alpha) * self.ema_latency)
                if self.ema_latency < 0.4:
                    self.limit = min(base_threads * 4, self.limit + 1)
                elif self.ema_latency > 1.2:
                    self.limit = max(1, self.limit - 1)
            self.cond.notify_all()

class ReapV2Engine:
    def __init__(self, start_url, output_dir, mode="app", js_snapshot=False, fast_mode=False, max_threads=8):
        self.start_url = normalize_url(start_url)
        self.parsed_start = urlparse(self.start_url)
        self.output_dir = output_dir or self.parsed_start.netloc
        self.temp_dir = os.path.join(self.output_dir, ".reap_temp")
        self.mode = mode
        self.js_snapshot = js_snapshot and not fast_mode
        self.fast_mode = fast_mode
        self.base_threads = max_threads
        self.base_netloc = self.parsed_start.netloc
        
        self.visited = set()
        self.route_map = {}
        self.asset_deps = {}
        self.failed_urls = []
        self.page_queue = asyncio.Queue()
        self.task_queue = asyncio.PriorityQueue() # Smart Parallel Pipeline
        
        self.domain_limits = {} # Adaptive Smart Concurrency
        self.asset_futures = {} # url -> asyncio.Future (Dependency Map)
        
        self.session = None
        self.browser = None
        self.context = None
        self.playwright = None
        self.running_tasks = []
        
        self.state_file = os.path.join(self.output_dir, ".reap_state.json")

    def _save_state_atomic(self):
        os.makedirs(self.output_dir, exist_ok=True)
        data = {
            "visited": list(self.visited),
            "timestamp": time.time()
        }
        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.output_dir, prefix=".reap_state_", suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, 'w') as f:
                json.dump(data, f)
            os.replace(tmp_path, self.state_file)
        except Exception:
            if os.path.exists(tmp_path): os.remove(tmp_path)

    def get_limiter(self, domain):
        if domain not in self.domain_limits:
            self.domain_limits[domain] = DynamicLimit(self.base_threads)
        return self.domain_limits[domain]

    async def init_session(self):
        conn = aiohttp.TCPConnector(limit=0, keepalive_timeout=60)
        self.session = aiohttp.ClientSession(
            connector=conn, 
            headers={"Connection": "keep-alive", "User-Agent": USER_AGENT}
        )
        if self.js_snapshot:
            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=True)
                self.context = await self.browser.new_context(user_agent=USER_AGENT)
            except ImportError:
                print_msg("Playwright not installed. JS snapshot disabled.", "error")
                self.js_snapshot = False

    async def close_session(self):
        if self.session: await self.session.close()
        if self.js_snapshot and self.browser:
            await self.browser.close()
            await self.playwright.stop()

    async def _warmup(self):
        try:
            async with self.session.head(self.start_url, timeout=5) as r: pass
        except Exception: pass

    async def fetch_page(self, url, max_retries=3):
        domain = urlparse(url).netloc
        limiter = self.get_limiter(domain)
        delay = 1
        
        for _ in range(max_retries):
            await limiter.acquire()
            start_time = time.time()
            try:
                if self.js_snapshot and self.context:
                    page = await self.context.new_page()
                    await page.goto(url, wait_until="networkidle")
                    html = await page.content()
                    await page.close()
                    await limiter.release()
                    return html
                else:
                    async with self.session.get(url, timeout=15) as response:
                        latency = time.time() - start_time
                        if response.status == 429:
                            await limiter.update_latency(latency, is_429=True, base_threads=self.base_threads)
                            await limiter.release()
                            await asyncio.sleep(delay)
                            delay *= 2
                            continue
                            
                        await limiter.update_latency(latency, base_threads=self.base_threads)
                        
                        if response.status == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                            res = await response.text()
                            await limiter.release()
                            return res
                        
                        await limiter.release()
                        return None
            except Exception:
                await limiter.release()
                await asyncio.sleep(delay)
                delay *= 2
        return None

    async def download_asset(self, url, max_retries=3):
        domain = urlparse(url).netloc
        limiter = self.get_limiter(domain)
        delay = 1
        
        temp_path = os.path.join(self.temp_dir, hashlib.md5(url.encode()).hexdigest() + ".tmp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        for _ in range(max_retries):
            await limiter.acquire()
            start_time = time.time()
            try:
                async with self.session.get(url, timeout=30) as response:
                    latency = time.time() - start_time
                    if response.status == 429:
                        await limiter.update_latency(latency, is_429=True, base_threads=self.base_threads)
                        await limiter.release()
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                        
                    await limiter.update_latency(latency, base_threads=self.base_threads)
                    
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        sha256 = hashlib.sha256()
                        with open(temp_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(65536):
                                f.write(chunk)
                                sha256.update(chunk)
                                
                        file_hash = sha256.hexdigest()
                        ext = os.path.splitext(urlparse(url).path)[1]
                        if not ext: ext = mimetypes.guess_extension(content_type.split(';')[0]) or ""
                        
                        final_fs_path = os.path.join(self.output_dir, "assets", f"{file_hash}{ext}")
                        final_url_path = f"/assets/{file_hash}{ext}"
                        
                        os.makedirs(os.path.dirname(final_fs_path), exist_ok=True)
                        shutil.move(temp_path, final_fs_path)
                        
                        await limiter.release()
                        return final_fs_path, final_url_path, content_type
                    await limiter.release()
                    return None, None, None
            except Exception:
                await limiter.release()
                if os.path.exists(temp_path): os.remove(temp_path)
                await asyncio.sleep(delay)
                delay *= 2
        return None, None, None

    async def get_or_download_asset(self, url, depth):
        if url in self.asset_futures:
            return await self.asset_futures[url]
        
        future = asyncio.Future()
        self.asset_futures[url] = future
        self.task_queue.put_nowait((get_priority(url), 'asset', url, depth))
        return await future

    async def process_page(self, url, depth):
        html = await self.fetch_page(url)
        if not html:
            self.failed_urls.append(url)
            return
        
        final_fs_path, local_url_path = get_page_local_path(url, self.output_dir, mode=self.mode)
        self.route_map[url] = local_url_path
        self.asset_deps[url] = []
        soup = BeautifulSoup(html, 'lxml')
        
        for script in soup.find_all('script'):
            if any(t in script.get('src', '').lower() for t in TRACKER_KEYWORDS): script.decompose()
        if self.mode == "reader":
            for tag in soup.find_all(['nav', 'footer', 'aside', 'iframe', 'script', 'style']): tag.decompose()
            
        stop_crawling = self.fast_mode and depth >= 1
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')): continue
            abs_url = normalize_url(urljoin(url, href))
            
            if not stop_crawling and is_same_domain(abs_url, self.base_netloc):
                if abs_url not in self.visited:
                    self.visited.add(abs_url)
                    self.task_queue.put_nowait((1, 'page', abs_url, depth + 1))
            
            anchor = '#' + href.split('#', 1)[1] if '#' in href else ''
            _, target_url_path = get_page_local_path(abs_url, self.output_dir, mode=self.mode)
            a['href'] = get_relative_url(local_url_path, target_url_path) + anchor
            
        # Extract assets and await their futures (Dependency Readiness Barrier)
        asset_replacements = []  # list of (tag, attr, abs_url)

        def queue_asset(tag, attr, val):
            if val.startswith('data:'):
                return
            abs_url = normalize_url(urljoin(url, val))

            if self.fast_mode and any(abs_url.lower().endswith(ext) for ext in HEAVY_EXTENSIONS):
                tag[attr] = ""
                return

            asset_replacements.append((tag, attr, abs_url))
            self.asset_deps[url].append(abs_url)

        asset_tags = {'img': ['src', 'data-src'], 'link': ['href'], 'script': ['src'], 'source': ['src'], 'video': ['src', 'poster'], 'audio': ['src']}
        for tag_name, attrs in asset_tags.items():
            for tag in soup.find_all(tag_name):
                for attr in attrs:
                    if tag.has_attr(attr): queue_asset(tag, attr, tag[attr])
                if tag.has_attr('srcset'):
                    # Simplify srcset to just the src logic for robustness during futures
                    parts = tag['srcset'].split(',')[0].strip().split()
                    if parts and not parts[0].startswith('data:'):
                        queue_asset(tag, 'srcset', parts[0])
                    
        for tag in soup.find_all(attrs={"data-bg": True}):
            queue_asset(tag, 'data-bg', tag['data-bg'])
            
        # Await all dependencies for this page
        if asset_replacements:
            coroutines = [self.get_or_download_asset(abs_url, depth) for _, _, abs_url in asset_replacements]
            results = await asyncio.gather(*coroutines, return_exceptions=True)

            for (tag, attr, abs_url), final_asset_url in zip(asset_replacements, results):
                if isinstance(final_asset_url, Exception) or not final_asset_url:
                    self.failed_urls.append(abs_url)
                    continue  # Keep original if failed
                tag[attr] = get_relative_url(local_url_path, final_asset_url)
            
        os.makedirs(os.path.dirname(final_fs_path), exist_ok=True)
        with open(final_fs_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        self._save_state_atomic()

    async def process_asset(self, url):
        fs_path, final_url_path, content_type = await self.download_asset(url)
        
        if not fs_path:
            self.failed_urls.append(url)
            self.asset_futures[url].set_result(None)
            return

        self.asset_deps[url] = []

        if content_type and 'text/css' in content_type and not self.fast_mode:
            with open(fs_path, 'r', encoding='utf-8', errors='ignore') as f:
                css_text = f.read()
                
            # Find dependencies in CSS
            css_deps = []
            def css_extract(match):
                asset_val = match.group(1).strip()
                if not asset_val.startswith("data:"):
                    abs_url = normalize_url(urljoin(url, asset_val))
                    css_deps.append(abs_url)
                    self.asset_deps[url].append(abs_url)
                return match.group(0)
                
            CSS_URL_PATTERN.sub(css_extract, css_text)
            
            # Wait for CSS dependencies
            dep_futures = [self.get_or_download_asset(dep_url, 0) for dep_url in css_deps]
            dep_results = await asyncio.gather(*dep_futures, return_exceptions=True)
            
            dep_map = {}
            for dep_url, result in zip(css_deps, dep_results):
                if not isinstance(result, Exception) and result:
                    dep_map[dep_url] = result
                    
            def css_replacer(match):
                asset_val = match.group(1).strip()
                if asset_val.startswith("data:"): return match.group(0)
                abs_url = normalize_url(urljoin(url, asset_val))
                if abs_url in dep_map:
                    return f"url('{get_relative_url(final_url_path, dep_map[abs_url])}')"
                return match.group(0)
                
            new_css = CSS_URL_PATTERN.sub(css_replacer, css_text)
            with open(fs_path, 'w', encoding='utf-8') as f:
                f.write(new_css)
                
        self.asset_futures[url].set_result(final_url_path)

    async def worker_loop(self):
        while True:
            task_type = None
            url = None
            try:
                priority, task_type, url, depth = await self.task_queue.get()
                if task_type == 'page':
                    await self.process_page(url, depth)
                elif task_type == 'asset':
                    # Only process if future is not already done (coalescing check)
                    if not self.asset_futures[url].done():
                        await self.process_asset(url)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if task_type == 'asset' and url and url in self.asset_futures and not self.asset_futures[url].done():
                    self.asset_futures[url].set_result(None)
            finally:
                self.task_queue.task_done()

    def _generate_404(self):
        p404 = os.path.join(self.output_dir, "404.html")
        html = f"""<!DOCTYPE html><html><head><title>Offline 404</title><style>body{{text-align:center;padding:50px;font-family:sans-serif;}}</style></head>
        <body><h1>Page Not Found</h1><p>This page was not downloaded during offline sync.</p>
        <a href="index.html">Return to Root</a></body></html>"""
        with open(p404, "w") as f: f.write(html)

    async def run(self):
        await self.init_session()
        await self._warmup()
        
        self.visited.add(self.start_url)
        self.task_queue.put_nowait((1, 'page', self.start_url, 0))
        
        self.running_tasks = [asyncio.create_task(self.worker_loop()) for _ in range(self.base_threads * 3)]
        
        # Wait for all priority queue tasks to finalize dependencies
        await self.task_queue.join()
        
        for w in self.running_tasks: w.cancel()
        await self.close_session()
        self._generate_404()
        
        # Generate unified manifest
        build_timestamp = time.time()
        
        # Hash fingerprint calculation
        assets_dir = os.path.join(self.output_dir, "assets")
        assets_list = [p for p in os.listdir(assets_dir) if not p.startswith(".")] if os.path.exists(assets_dir) else []
        build_hash_ctx = hashlib.sha256()
        for a in sorted(assets_list): build_hash_ctx.update(a.encode())
        for r in sorted(self.route_map.values()): build_hash_ctx.update(r.encode())
        
        manifest_path = os.path.join(self.output_dir, "manifest.json")
        manifest_data = {
            "version": __version__,
            "timestamp": build_timestamp,
            "build_hash": build_hash_ctx.hexdigest()[:16],
            "entry": "index.html",
            "mode": self.mode,
            "base_path": "/",
            "routes": list(self.visited),
            "route_mapping": self.route_map,
            "assets": assets_list,
            "asset_dependencies": self.asset_deps
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
            
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

def archive_site(url, output_dir, mode="app", js_snapshot=False, fast_mode=False, threads=8, verbose=True):
    if USE_RICH and verbose:
        panel_content = (
            f"[bold gold3]Target URL:[/bold gold3] {url}\n"
            f"[bold gold3]Output Dir:[/bold gold3] {output_dir or urlparse(url).netloc}\n"
            f"[bold gold3]Mode:[/bold gold3] {mode}\n"
            f"[bold gold3]JS Snapshot:[/bold gold3] {'Enabled' if js_snapshot and not fast_mode else 'Disabled'}\n"
            f"[bold gold3]Engine:[/bold gold3] v{__version__} (Smart Pipeline)"
        )
        console.print(Panel(panel_content, title=f"[bold gold3]🌾 reap v{__version__}[/bold gold3]", border_style="gold3", expand=False))
        
    engine = ReapV2Engine(url, output_dir, mode, js_snapshot, fast_mode, threads)
    
    if USE_RICH and verbose:
        with console.status("[bold gold3]Reconstructing offline replica...", spinner="aesthetic"):
            asyncio.run(engine.run())
    else:
        if verbose:
            print(f"Scraping {url} with v{__version__} engine...")
        asyncio.run(engine.run())
        
    if verbose:
        print_msg(f"v{__version__} reconstruction completed successfully.", "success")
    return engine.output_dir, engine.failed_urls
