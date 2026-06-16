import sys
from reap.cli import parse_args
from reap.utils import print_msg

def main():
    args = parse_args()

    # Route 1: Serve an existing folder directly
    if not args.url and args.serve and args.output:
        from reap.server import serve_directory
        serve_directory(args.output, args.port)
        return
    elif not args.url:
        print_msg("Error: No URL provided. Run 'reap --help' for usage instructions.", "error")
        sys.exit(1)

    # Route 2: Standalone Watch/Diff Check (if previously downloaded)
    if args.watch and not args.download_now:
        from reap.watcher import check_changes
        check_changes(args.url, args.output)
        return

    # Route 3: Standard Scrape Pipeline
    from reap.engine import archive_site
    output_dir = archive_site(args.url, args.output, args.fast, args.threads)

    # Post-Processing Pipeline
    if args.optimize:
        from reap.optimizer import optimize_assets
        optimize_assets(output_dir)

    if args.single_file:
        from reap.singlefile import bundle_to_single_file
        bundle_to_single_file(output_dir)

    if args.zip:
        from reap.utils import package_directory
        package_directory(output_dir)

    if args.serve:
        from reap.server import serve_directory
        serve_directory(output_dir, args.port)

if __name__ == "__main__":
    main()