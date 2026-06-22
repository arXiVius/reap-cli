import shutil
import sys

from reap import __version__

VERBOSE = True


def set_verbose(is_verbose):
    global VERBOSE
    VERBOSE = is_verbose


try:
    from rich.console import Console
    from rich.text import Text

    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False


def print_banner():
    """Prints a minimal, branded startup line — identity at the edges, not noise."""
    if USE_RICH:
        try:
            console.print(
                f"[bold gold3]🌾 reap[/bold gold3] [dim]v{__version__}[/dim]"
                f"  [dim italic]- web reconstruction engine[/dim italic]"
            )
            console.print("[dim]Build. Reconstruct. Deploy.[/dim]\n")
        except UnicodeEncodeError:
            print(f"reap v{__version__} - web reconstruction engine")
            print("Build. Reconstruct. Deploy.\n")
    else:
        print(f"reap v{__version__} - web reconstruction engine")
        print("Build. Reconstruct. Deploy.\n")


def _safe_text(text):
    """Gracefully handle emoji/unicode on terminals that can't render them (e.g. Windows cp1252)."""
    try:
        text.encode(sys.stdout.encoding or "utf-8")
        return text
    except (UnicodeEncodeError, LookupError):
        import re
        return re.sub(r'[\U0001f300-\U0001fAFF]', '', text).replace('—', '-').strip()


def print_msg(text, status_type="info"):
    global VERBOSE
    if not VERBOSE and status_type not in ("error", "interrupt", "success"):
        return

    safe_t = _safe_text(text)

    if USE_RICH:
        theme = {
            "info": "cyan",
            "success": "green bold",
            "error": "red bold",
            "warning": "yellow",
            "interrupt": "orange3 bold",
        }
        color = theme.get(status_type, "white")
        try:
            console.print(safe_t, style=color)
        except UnicodeEncodeError:
            print(safe_t)
    else:
        prefixes = {
            "info": "[*]",
            "success": "[+]",
            "error": "[-]",
            "warning": "[!]",
            "interrupt": "[!]",
        }
        print(f"{prefixes.get(status_type, 'info')} {safe_t}")


def package_directory(directory):
    print_msg(f"Packaging {directory} into zip...", "info")
    try:
        shutil.make_archive(directory, "zip", directory)
        print_msg(f"Created archive: {directory}.zip", "success")
    except Exception as e:
        print_msg(f"Compression failed: {e}", "error")