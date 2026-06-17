import shutil
import sys

try:
    from rich.console import Console
    from rich.text import Text
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

ASCII_ART = r"""
  _ __ ___   __ _  _ __  
 | '__/ _ \ / _` || '_ \ 
 | | |  __/| (_| || |_) |
 |_|  \___| \__,_|| .__/ 
                  |_|    
"""

def print_banner():
    """Prints the branded ASCII banner with a warm wheat/gold gradient."""
    if USE_RICH:
        # Wheat/Gold-themed gradient styling
        styled_text = Text(ASCII_ART, style="gold3 bold")
        console.print(styled_text)
        console.print("[dim]🌾 A modern CLI for harvesting and refining the web[/dim]\n")
    else:
        print("reap - 🌾 Harvest the web. Refine it locally.")

def print_msg(text, status_type="info"):
    if USE_RICH:
        theme = {
            "info": "cyan",
            "success": "green bold",
            "error": "red bold",
            "warning": "yellow",
            "interrupt": "orange3 bold"
        }
        color = theme.get(status_type, "white")
        console.print(text, style=color)
    else:
        prefixes = {
            "info": "[*]", 
            "success": "[+]", 
            "error": "[-]", 
            "warning": "[!]",
            "interrupt": "[!]"
        }
        print(f"{prefixes.get(status_type, 'info')} {text}")

def package_directory(directory):
    print_msg(f"Packaging {directory} into zip...", "info")
    try:
        shutil.make_archive(directory, 'zip', directory)
        print_msg(f"Created archive: {directory}.zip", "success")
    except Exception as e:
        print_msg(f"Compression failed: {e}", "error")