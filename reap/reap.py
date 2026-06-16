#!/usr/bin/env python3
import argparse
import http.server
import os
import shutil
import socketserver
import subprocess
import sys
from urllib.parse import urlparse

try:
    from rich.console import Console
    from rich.panel import Panel
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEAVY_EXTENSIONS = "mp4,mp3,wav,avi,mkv,zip,tar,gz,rar,pdf,dmg,exe,apk,iso"

def print_msg(text, status_type="info"):
    if USE_RICH:
        theme = {"info": "cyan", "success": "green bold", "error": "red bold", "warning": "yellow"}
        console.print(text, style=theme.get(status_type, "white"))
    else:
        prefixes = {"info": "[*]", "success": "[+]", "error": "[-]", "warning": "[!]"}
        print(f"{prefixes.get(status_type, '')} {text}")

def detect_engine():
    if shutil.which("wget2"):
        return "wget2"
    elif shutil.which("wget"):
        return "wget"
    return None

def archive_site(url, output_dir, fast_mode, threads):
    engine = detect_engine()
    if not engine:
        print_msg("Error: Neither 'wget' nor 'wget2' was found in your PATH.", "error")
        sys.exit(1)

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print_msg(f"Invalid URL: '{url}'. Please include the protocol (e.g., https://).", "error")
        sys.exit(1)

    destination = output_dir if output_dir else parsed_url.netloc
    log_file = "reap-engine.log"

    cmd = [
        engine,
        "--mirror",
        "--convert-links",
        "--page-requisites",
        "--no-parent",
        "--adjust-extension",
        "--span-hosts",
        f"--domains={parsed_url.netloc},framerusercontent.com,fonts.googleapis.com,fonts.gstatic.com",
        f"--user-agent={USER_AGENT}",
        "--timeout=5",
        "--tries=2",
        "-o", log_file
    ]

    if engine == "wget2":
        cmd.append(f"--max-threads={threads}")

    if fast_mode:
        cmd.append(f"--reject={HEAVY_EXTENSIONS}")

    if output_dir:
        cmd.extend(["-P", output_dir])

    cmd.append(url)

    if USE_RICH:
        features_list = []
        if engine == "wget2":
            features_list.append(f"[green]✓ Multithreading enabled ({threads} threads via wget2)[/green]")
        else:
            features_list.append("[yellow]⚠ Using single-threaded wget (Install wget2 for faster speeds)[/yellow]")
        
        if fast_mode:
            features_list.append("[cyan]✓ Fast Mode active (skipping large media archives/videos)[/cyan]")

        panel_content = (
            f"[bold]Target:[/bold] {url}\n"
            f"[bold]Output Directory:[/bold] {destination}\n"
            f"[bold]Engine:[/bold] {engine}\n"
            f"[bold]Status Log:[/bold] {log_file}\n\n" +
            "\n".join(features_list)
        )
        console.print(Panel(panel_content, title="[bold blue]Reap - Web Harvester[/bold blue]", border_style="blue", expand=False))

        try:
            with console.status("[bold green]Harvesting website...", spinner="dots"):
                subprocess.run(cmd, check=True)
            print_msg(f"Successfully reaped site to: {destination}", "success")
        except subprocess.CalledProcessError as e:
            print_msg(f"Finished with issues. Exit code: {e.returncode}. Check {log_file} for details.", "warning")
    else:
        print(f"Reaping {url} using {engine}...")
        subprocess.run(cmd)

    return destination

def serve_directory(directory, port=8000):
    if not os.path.exists(directory):
        print_msg(f"Error: Directory '{directory}' does not exist. Cannot serve.", "error")
        return

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print_msg(f"\nLocal server active at: http://localhost:{port}", "success")
            print_msg("Press Ctrl+C to stop the server.", "info")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print_msg("\nServer stopped.", "info")
    except Exception as e:
        print_msg(f"Failed to start local server: {e}", "error")

def package_directory(directory):
    print_msg(f"Archiving directory into {directory}.zip...", "info")
    try:
        shutil.make_archive(directory, 'zip', directory)
        print_msg(f"Created archive: {directory}.zip", "success")
    except Exception as e:
        print_msg(f"Failed to create zip: {e}", "error")

def main():
    parser = argparse.ArgumentParser(
        description="reap: An enhanced site mirroring tool featuring speed tuning, file exclusions, and offline serving."
    )
    parser.add_argument("url", nargs="?", help="The URL of the website to download")
    parser.add_argument("-o", "--output", help="Specify custom destination folder", default=None)
    parser.add_argument("-f", "--fast", action="store_true", help="Skip heavy media/archive files for faster download")
    parser.add_argument("-t", "--threads", type=int, default=8, help="Max threads to use (only works if wget2 is installed)")
    parser.add_argument("-z", "--zip", action="store_true", help="Compress the final output into a .zip file")
    parser.add_argument("-s", "--serve", action="store_true", help="Instantly launch a local web server to view the output")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the local server on")

    args = parser.parse_args()

    if not args.url and args.serve and args.output:
        serve_directory(args.output, args.port)
        return
    elif not args.url:
        parser.print_help()
        sys.exit(1)

    output_dir = archive_site(args.url, args.output, args.fast, args.threads)

    if args.zip:
        package_directory(output_dir)

    if args.serve:
        serve_directory(output_dir, args.port)

if __name__ == "__main__":
    main()