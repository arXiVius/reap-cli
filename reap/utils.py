import shutil

try:
    from rich.console import Console
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

def print_msg(text, status_type="info"):
    if USE_RICH:
        theme = {"info": "cyan", "success": "green bold", "error": "red bold", "warning": "yellow"}
        console.print(text, style=theme.get(status_type, "white"))
    else:
        prefixes = {"info": "[*]", "success": "[+]", "error": "[-]", "warning": "[!]"}
        print(f"{prefixes.get(status_type, '')} {text}")

def package_directory(directory):
    print_msg(f"Packaging {directory} into zip...", "info")
    try:
        shutil.make_archive(directory, 'zip', directory)
        print_msg(f"Created archive: {directory}.zip", "success")
    except Exception as e:
        print_msg(f"Compression failed: {e}", "error")