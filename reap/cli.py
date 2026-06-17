import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="reap: An extensible, modular CLI web harvester and archiver."
    )
    # Positioning argument optional so --explore can run alone
    parser.add_argument("url", nargs="?", help="The URL of the website to process")
    parser.add_argument("-o", "--output", help="Custom output directory path", default=None)
    parser.add_argument("-f", "--fast", action="store_true", help="Fast mode: skip heavy media/archives")
    parser.add_argument("-t", "--threads", type=int, default=8, help="Concurrency limit (wget2 only)")
    parser.add_argument("-s", "--serve", action="store_true", help="Start local web server after harvesting")
    parser.add_argument("--port", type=int, default=8000, help="Local server port")
    parser.add_argument("-z", "--zip", action="store_true", help="Zip the output directory")
    
    # Advanced Features
    parser.add_argument("--optimize", action="store_true", help="Convert images to optimized WebP format")
    parser.add_argument("--single-file", action="store_true", help="Bundle the static output into a single HTML file")
    parser.add_argument("--watch", action="store_true", help="Monitor a site and diff against local archives")
    parser.add_argument("--download-now", action="store_true", help="Force download during a watch pass")
    
    # New Modular Features
    parser.add_argument("--clean", action="store_true", help="Privacy Shield: Strip third-party trackers & cookie overlays")
    parser.add_argument("--audit", action="store_true", help="Diagnostic Audit: Find broken links & assets in the offline copy")
    parser.add_argument("--deploy", action="store_true", help="One-click static deployment upload directly to Netlify")
    parser.add_argument("--explore", action="store_true", help="Launch interactive terminal dashboard to manage saved sites")

    return parser.parse_args()