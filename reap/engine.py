import shutil
import subprocess
import sys
from urllib.parse import urlparse
from reap.utils import print_msg

try:
    from rich.console import Console
    from rich.panel import Panel
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEAVY_EXTENSIONS = "mp4,mp3,wav,avi,mkv,zip,tar,gz,rar,pdf,dmg,exe,apk,iso"

def detect_engine():
    if shutil.which("wget2"):
        return "wget2"
    elif shutil.which("wget"):
        return "wget"
    return None

def archive_site(url, output_dir, fast_mode, threads):
    engine = detect_engine()
    if not engine:
        print_msg("Error: 'wget' or 'wget2' must be installed.", "error")
        sys.exit(1)

    parsed_url = urlparse(url)
    destination = output_dir if output_dir else parsed_url.netloc
    log_file = "reap-engine.log"

    cmd = [
        engine, "--mirror", "--convert-links", "--page-requisites",
        "--no-parent", "--adjust-extension", "--span-hosts",
        f"--domains={parsed_url.netloc},framerusercontent.com,fonts.googleapis.com,fonts.gstatic.com",
        f"--user-agent={USER_AGENT}", "--timeout=5", "--tries=2", "-o", log_file
    ]

    if engine == "wget2":
        cmd.append(f"--max-threads={threads}")
    if fast_mode:
        cmd.append(f"--reject={HEAVY_EXTENSIONS}")
    if output_dir:
        cmd.extend(["-P", output_dir])
    cmd.append(url)

    if USE_RICH:
        panel_content = f"[bold]Target URL:[/bold] {url}\n[bold]Output:[/bold] {destination}\n[bold]Engine:[/bold] {engine}"
        console.print(Panel(panel_content, title="[bold blue]Reap Scraper[/bold blue]", border_style="blue", expand=False))
        try:
            with console.status("[bold green]Crawling assets...", spinner="dots"):
                subprocess.run(cmd, check=True)
            print_msg("Scrape operation completed successfully.", "success")
        except subprocess.CalledProcessError:
            print_msg(f"Finished with issues. Check {log_file} for details.", "warning")
    else:
        print(f"Scraping {url}...")
        subprocess.run(cmd)

    return destination