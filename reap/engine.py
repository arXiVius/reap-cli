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

    # Strict silence configuration
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
        panel_content = (
            f"[bold gold3]Target URL:[/bold gold3] {url}\n"
            f"[bold gold3]Output Dir:[/bold gold3] {destination}\n"
            f"[bold gold3]Scrape Engine:[/bold gold3] {engine}\n"
            f"[bold gold3]Verbose Log:[/bold gold3] {log_file}"
        )
        console.print(Panel(panel_content, title="[bold gold3]Reap Scraper[/bold gold3]", border_style="gold3", expand=False))
        
        # Open the log file to dump standard output streams and keep terminal quiet
        with open(log_file, "a", encoding="utf-8") as f_log:
            try:
                # Use Popen to allow background task killing on manual interrupt
                process = subprocess.Popen(cmd, stdout=f_log, stderr=f_log)
                
                with console.status("[bold gold3]Harvesting assets from site structure...", spinner="aesthetic") as status:
                    process.wait()
                
                if process.returncode == 0:
                    print_msg("Scrape operation completed successfully.", "success")
                else:
                    print_msg(f"Completed with warnings. System exited with code {process.returncode}.", "warning")
            except KeyboardInterrupt:
                process.terminate()  # Safely terminate the running wget process
                raise KeyboardInterrupt  # Pass the exception up to main handler
    else:
        print(f"Scraping {url}...")
        try:
            process = subprocess.Popen(cmd)
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            raise KeyboardInterrupt

    return destination