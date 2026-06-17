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
    """Scans and verifies that all local links and media files exist on the disk."""
    print_msg("Initiating structural asset integrity audit...", "info")
    
    broken_assets = []
    scanned_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".html", ".htm", ".css")):
                scanned_count += 1
                full_path = os.path.join(root, file)
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    matches = re.findall(LINK_PATTERN, content)
                    for match in matches:
                        # Skip external URLs, anchors, mailto, and base64 structures
                        if match.startswith(("http", "https", "#", "mailto:", "data:", "tel:")):
                            continue
                        
                        # Normalize URL path encoding
                        decoded_match = unquote(match).split("?")[0].split("#")[0]
                        if not decoded_match:
                            continue

                        # Resolve absolute local path
                        resolved_path = os.path.abspath(os.path.join(root, decoded_match))
                        
                        if not os.path.exists(resolved_path):
                            broken_assets.append({
                                "file": os.path.relpath(full_path, directory),
                                "target": decoded_match
                            })
                except Exception as e:
                    print_msg(f"Audit skipped for {file}: {e}", "warning")

    # Render results
    if broken_assets:
        print_msg(f"Audit found {len(broken_assets)} broken assets across {scanned_count} files.", "warning")
        
        if USE_RICH:
            table = Table(title="Broken Local Assets", show_header=True, header_style="bold red")
            table.add_column("Source File", style="cyan")
            table.add_column("Missing Target Link/Asset", style="yellow")
            
            for item in broken_assets:
                table.add_row(item["file"], item["target"])
            console.print(table)
        else:
            for item in broken_assets:
                print(f"[!] Broken Asset: {item['file']} -> Missing: {item['target']}")
    else:
        print_msg(f"Perfect Audit: All local resources exist across {scanned_count} analyzed files.", "success")