import os
from reap.utils import print_msg

def optimize_assets(directory):
    """Finds downloaded PNG/JPG files and converts them to optimized WebP format."""
    try:
        from PIL import Image
    except ImportError:
        print_msg("Skipping optimization: 'Pillow' is not installed.", "warning")
        print_msg("Install optional dependencies with: pip install 'reap-cli[optimize]'", "info")
        return

    print_msg("Scanning directory for image optimizations...", "info")
    optimized_count = 0
    saved_bytes = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, file)
                original_size = os.path.getsize(full_path)
                webp_path = os.path.splitext(full_path)[0] + ".webp"

                try:
                    with Image.open(full_path) as im:
                        im.save(webp_path, "WEBP", quality=80)
                    
                    webp_size = os.path.getsize(webp_path)
                    
                    if webp_size < original_size:
                        os.remove(full_path)  # Delete original
                        optimized_count += 1
                        saved_bytes += (original_size - webp_size)
                    else:
                        os.remove(webp_path)  # Keep original if smaller
                except Exception as e:
                    print_msg(f"Failed to optimize {file}: {e}", "warning")

    if optimized_count > 0:
        saved_mb = saved_bytes / (1024 * 1024)
        print_msg(f"Optimized {optimized_count} images. Saved {saved_mb:.2f} MB of disk space.", "success")
    else:
        print_msg("No compressible images found.", "info")