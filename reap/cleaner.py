import os
import re
from reap.utils import print_msg

# Common tracking / analytics / cookie consent patterns
TRACKER_PATTERNS = [
    r'<script[^>]*>(?:[\s\S]*?(?:googletagmanager|google-analytics|fbevents|hotjar|intercom|hs-scripts|crisp|cookie-banner|cookieconsent)[\s\S]*?)</script>',
    r'<noscript[^>]*>(?:[\s\S]*?(?:facebook\.com/tr|google-analytics|googletagmanager)[\s\S]*?)</noscript>',
]

# Common ID/Class selectors for cookie consent banner overlays
BANNER_PATTERNS = [
    r'<div[^>]*?(?:id|class)="[^"]*?(?:cookie|consent|privacy-banner)[^"]*"[^>]*?>[\s\S]*?<\/div>'
]

def sanitize_html_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original_len = len(content)

        # Remove tracker script blocks
        for pattern in TRACKER_PATTERNS:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)

        # Remove cookie banner overlays
        for pattern in BANNER_PATTERNS:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)

        if len(content) < original_len:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except Exception as e:
        print_msg(f"Could not sanitize {os.path.basename(file_path)}: {e}", "warning")
    return False

def clean_assets(directory):
    """Walks the directory and strips third-party trackers and banners from HTML files."""
    print_msg("Scanning assets to strip trackers, cookies, and chat widgets...", "info")
    cleaned_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                full_path = os.path.join(root, file)
                if sanitize_html_file(full_path):
                    cleaned_count += 1

    if cleaned_count > 0:
        print_msg(f"Privacy Shield: Cleaned tracking data and banners from {cleaned_count} HTML files.", "success")
    else:
        print_msg("No tracking scripts or cookie banners detected.", "info")