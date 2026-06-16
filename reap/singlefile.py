import os
import re
import base64
import mimetypes
from reap.utils import print_msg

def get_base64_data_uri(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    try:
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded}"
    except Exception:
        return ""

def bundle_to_single_file(directory):
    """Finds index.html and compiles referenced assets into one file."""
    print_msg("Initiating single-file compilation...", "info")
    
    # Try to locate primary entrypoint HTML file
    html_path = os.path.join(directory, "index.html")
    if not os.path.exists(html_path):
        # Fallback: find any HTML file
        html_files = [os.path.join(r, f) for r, _, fs in os.walk(directory) for f in fs if f.endswith(".html")]
        if not html_files:
            print_msg("Compile error: No HTML entry point found.", "error")
            return
        html_path = html_files[0]

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple inline CSS helper
        def inline_css(match):
            href = match.group(1)
            full_css_path = os.path.abspath(os.path.join(os.path.dirname(html_path), href))
            if os.path.exists(full_css_path):
                try:
                    with open(full_css_path, "r", encoding="utf-8") as css_file:
                        return f"<style>{css_file.read()}</style>"
                except Exception:
                    pass
            return match.group(0)

        # Simple inline Image helper
        def inline_img(match):
            src = match.group(1)
            full_img_path = os.path.abspath(os.path.join(os.path.dirname(html_path), src))
            if os.path.exists(full_img_path):
                data_uri = get_base64_data_uri(full_img_path)
                if data_uri:
                    return f'src="{data_uri}"'
            return match.group(0)

        # Regex replacements (basic offline bundle compile)
        content = re.sub(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>', inline_css, content)
        content = re.sub(r'src="([^"]+\.(?:png|jpg|jpeg|gif|svg|webp))"', inline_img, content)

        bundle_output = os.path.join(directory, "compiled_bundle.html")
        with open(bundle_output, "w", encoding="utf-8") as f:
            f.write(content)

        print_msg(f"Bundle successfully compiled to: {bundle_output}", "success")
    except Exception as e:
        print_msg(f"Failed to bundle single-file: {e}", "error")