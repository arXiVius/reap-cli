import argparse
import sys

from reap import __version__, __author__, __url__, __description__


def _safe_text(text):
    """Gracefully handle emoji/unicode on terminals that can't render them (e.g. Windows cp1252)."""
    try:
        text.encode(sys.stdout.encoding or "utf-8")
        return text
    except (UnicodeEncodeError, LookupError):
        # Strip common emoji, keep the rest
        import re
        return re.sub(r'[\U0001f300-\U0001fAFF]', '', text).strip()


def _version_string():
    return (
        f"reap v{__version__}\n"
        f"built by {__author__}\n"
        f"{__url__}"
    )


def _about_panel():
    """Full project info panel — the discoverable credit layer."""
    wheat = _safe_text("🌾")
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        content = (
            f"[bold gold3]{wheat} reap[/bold gold3]\n\n"
            f"{__description__}\n\n"
            f"[dim]Version:[/dim]  {__version__}\n"
            f"[dim]Author:[/dim]   {__author__}\n"
            f"[dim]GitHub:[/dim]   {__url__}\n"
            f"[dim]License:[/dim]  MIT"
        )
        try:
            console.print(Panel(content, border_style="gold3", expand=False, padding=(1, 3)))
        except UnicodeEncodeError:
            # Fallback for terminals that can't render Rich + emoji
            _about_plain()
    except ImportError:
        _about_plain()


def _about_plain():
    """Plain-text fallback for --about on limited terminals."""
    print(f"\nreap\n")
    print(f"{__description__}\n")
    print(f"Version:  {__version__}")
    print(f"Author:   {__author__}")
    print(f"GitHub:   {__url__}")
    print(f"License:  MIT\n")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="reap",
        description="reap - web reconstruction engine\nBuild. Reconstruct. Deploy.",
        epilog=f"reap v{__version__}  |  {__url__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=_version_string(),
    )
    parser.add_argument(
        "--about",
        action="store_true",
        help="Show full project info and credits",
    )

    # Positional argument optional so --explore / --about can run alone
    parser.add_argument("url", nargs="?", help="The URL of the website to process")

    # ── Build Options ─────────────────────────────────────────────────
    build_group = parser.add_argument_group("Build Options")
    build_group.add_argument(
        "--mode",
        choices=["mirror", "app", "reader", "fast"],
        default="app",
        help="Reconstruction mode (default: app)",
    )
    build_group.add_argument(
        "--js",
        action="store_true",
        help="Enable JS snapshot mode (requires playwright)",
    )
    build_group.add_argument(
        "-f", "--fast",
        action="store_true",
        help="Fast mode: skip heavy media/archives",
    )
    build_group.add_argument(
        "--clean",
        action="store_true",
        help="Privacy shield: strip third-party trackers & cookie overlays",
    )
    build_group.add_argument(
        "-t", "--threads",
        type=int,
        default=8,
        help="Concurrency base limit (default: 8)",
    )

    # ── Output Options ────────────────────────────────────────────────
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        help="Custom output directory path",
        default=None,
    )
    output_group.add_argument(
        "-z", "--zip",
        action="store_true",
        help="Zip the output directory",
    )
    output_group.add_argument(
        "--optimize",
        action="store_true",
        help="Convert images to optimized WebP format",
    )
    output_group.add_argument(
        "--single-file",
        action="store_true",
        help="Bundle the static output into a single HTML file",
    )

    # ── Deployment & Server ───────────────────────────────────────────
    deploy_group = parser.add_argument_group("Deployment & Server")
    deploy_group.add_argument(
        "--deploy",
        nargs="?",
        const="auto",
        choices=["vercel", "netlify", "cf", "auto"],
        help="Deploy the built site to a provider",
    )
    deploy_group.add_argument(
        "-s", "--serve",
        action="store_true",
        help="Start local web server after harvesting",
    )
    deploy_group.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Local server port (default: 8000)",
    )

    # ── UX & Interaction ──────────────────────────────────────────────
    ux_group = parser.add_argument_group("UX & Interaction")
    ux_group.add_argument(
        "--verbose",
        action="store_true",
        help="Disable sleek mode and show full logs",
    )
    ux_group.add_argument(
        "--audit",
        action="store_true",
        help="Diagnostic audit: find broken links & assets",
    )
    ux_group.add_argument(
        "--explore",
        action="store_true",
        help="Launch interactive terminal dashboard",
    )
    ux_group.add_argument(
        "--watch",
        action="store_true",
        help="Monitor a site and diff against local archives",
    )
    ux_group.add_argument(
        "--download-now",
        action="store_true",
        help="Force download during a watch pass",
    )

    args = parser.parse_args()

    # Handle --about before any URL checks
    if args.about:
        _about_panel()
        sys.exit(0)

    return args