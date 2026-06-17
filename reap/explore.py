import os
import sys
from reap.utils import print_msg

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

def list_harvested_sites():
    """Scans current working directory for folders containing index.html files."""
    folders = []
    for entry in os.scandir("."):
        if entry.is_dir() and not entry.name.startswith((".", "_", "reap-")):
            html_index = os.path.join(entry.path, "index.html")
            if os.path.exists(html_index):
                folders.append(entry.name)
    return folders

def run_explorer():
    """Launches the interactive TUI choice console."""
    print_msg("Opening Interactive Dashboard...", "info")
    
    while True:
        sites = list_harvested_sites()
        if not sites:
            print_msg("Explorer: No downloaded sites found in current directory.", "warning")
            return

        print_msg("\n[bold gold3]🌾 Harvested Archives Explorer[/bold gold3]", "info")
        
        if USE_RICH:
            table = Table(show_header=True, header_style="bold gold3")
            table.add_column("ID", style="dim", width=4)
            table.add_column("Site Name (Directory)", style="cyan")
            table.add_column("Size", style="magenta")
            
            for i, site in enumerate(sites, 1):
                # Calculate size
                size_bytes = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(site) for f in fs)
                size_mb = size_bytes / (1024 * 1024)
                table.add_row(str(i), site, f"{size_mb:.2f} MB")
            
            console.print(table)
        else:
            for i, site in enumerate(sites, 1):
                print(f"[{i}] {site}")

        print("\nActions: [number] Select Site  |  [q] Quit Explorer")
        choice = input("Enter choice: ").strip().lower()

        if choice == "q":
            print_msg("Closing Explorer.", "info")
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sites):
                selected_site = sites[idx]
                handle_site_actions(selected_site)
            else:
                print_msg("Invalid directory index.", "error")
        except ValueError:
            print_msg("Please enter a numeric ID or 'q'.", "error")

def handle_site_actions(site_dir):
    """Processes interactive actions for a chosen directory."""
    while True:
        print_msg(f"\nSite Focus: [bold cyan]{site_dir}[/bold cyan]", "info")
        print("1. Launch local serve preview")
        print("2. Optimize images (WebP conversion)")
        print("3. Integrity check (Audit local assets)")
        print("4. Compress to ZIP")
        print("5. Deploy static folder to Netlify")
        print("6. Return to selection menu")
        
        choice = input("Select Action (1-6): ").strip()
        
        if choice == "1":
            from reap.server import serve_directory
            serve_directory(site_dir)
        elif choice == "2":
            from reap.optimizer import optimize_assets
            optimize_assets(site_dir)
        elif choice == "3":
            from reap.audit import audit_directory
            audit_directory(site_dir)
        elif choice == "4":
            from reap.utils import package_directory
            package_directory(site_dir)
        elif choice == "5":
            from reap.deploy import deploy_to_netlify
            deploy_to_netlify(site_dir)
        elif choice == "6":
            break
        else:
            print_msg("Invalid choice.", "error")