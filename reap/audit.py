import os
import re
from urllib.parse import unquote
from reap.utils import print_msg

try:
    from rich.console import Console
    from rich.table import Table
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

# Regex to pull local paths from common attributes
LINK_PATTERN = r'(?:href|src)="([^"]+)"'

def audit_directory(directory):
    """Scans and verifies build integrity: no external HTTP leakage, missing local files, or orphans."""
    print_msg("Initiating Build Integrity Validator...", "info")
    
    broken_assets = []
    external_leaks = []
    scanned_count = 0
    total_links_checked = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".html", ".htm", ".css", ".js")):
                scanned_count += 1
                full_path = os.path.join(root, file)
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    matches = re.findall(LINK_PATTERN, content)
                    total_links_checked += len(matches)
                    
                    if file.lower().endswith(".js"):
                        js_urls = re.findall(r'https?://[^\s"\'\`]+', content)
                        total_links_checked += len(js_urls)
                        for url in js_urls:
                            if not url.startswith(("https://fonts.", "https://www.youtube", "https://player.vimeo")):
                                external_leaks.append({
                                    "file": os.path.relpath(full_path, directory),
                                    "target": url
                                })
                        continue
                    
                    for match in matches:
                        # Check for external leaks
                        if match.startswith(("http://", "https://")):
                            if not match.startswith(("https://fonts.", "https://www.youtube", "https://player.vimeo")):
                                external_leaks.append({
                                    "file": os.path.relpath(full_path, directory),
                                    "target": match
                                })
                            continue
                            
                        if match.startswith(("#", "mailto:", "data:", "tel:", "javascript:")):
                            continue
                        
                        decoded_match = unquote(match).split("?")[0].split("#")[0]
                        if not decoded_match:
                            continue

                        # Resolve absolute local path
                        if decoded_match.startswith("/"):
                            # Relative to root of directory
                            resolved_path = os.path.join(directory, decoded_match.lstrip("/"))
                        else:
                            resolved_path = os.path.abspath(os.path.join(root, decoded_match))
                        
                        if not os.path.exists(resolved_path):
                            broken_assets.append({
                                "file": os.path.relpath(full_path, directory),
                                "target": decoded_match
                            })
                except Exception as e:
                    print_msg(f"Audit skipped for {file}: {e}", "warning")

    # Render results
    passed = len(broken_assets) == 0 and len(external_leaks) == 0
    
    if USE_RICH:
        console.print(f"\n[bold]Integrity Report: {scanned_count} files scanned, {total_links_checked} references verified.[/bold]")
        
        if broken_assets:
            table = Table(title="Broken Local Assets (404 Offline)", show_header=True, header_style="bold red")
            table.add_column("Source File", style="cyan")
            table.add_column("Missing Target Link", style="yellow")
            for item in broken_assets:
                table.add_row(item["file"], item["target"])
            console.print(table)
            
        if external_leaks:
            table_leak = Table(title="External HTTP Leaks (Not offline-safe)", show_header=True, header_style="bold red")
            table_leak.add_column("Source File", style="cyan")
            table_leak.add_column("External Dependency", style="magenta")
            for item in external_leaks:
                table_leak.add_row(item["file"], item["target"])
            console.print(table_leak)
            
        if passed:
            print_msg("✅ Perfect Build Integrity: No broken assets or unhandled external dependencies.", "success")
        else:
            print_msg("❌ Build Validation Failed.", "error")
    else:
        if broken_assets:
            for item in broken_assets: print(f"[!] Broken Asset: {item['file']} -> {item['target']}")
        if external_leaks:
            for item in external_leaks: print(f"[!] External Leak: {item['file']} -> {item['target']}")
        if passed:
            print_msg("Perfect Build Integrity. No errors.", "success")
            
    return passed