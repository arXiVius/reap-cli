import sys
from reap.cli import parse_args
from reap.utils import print_msg, print_banner

def main():
    print_banner()
    args = parse_args()

    try:
        # Route 1: TUI Explorer Dashboard
        if args.explore:
            from reap.explore import run_explorer
            run_explorer()
            return

        # Route 2: Serve folder directly
        if not args.url and args.serve and args.output:
            from reap.server import serve_directory
            serve_directory(args.output, args.port)
            return
        elif not args.url:
            print_msg("Error: No URL provided. Run 'reap --help' or 'reap --explore' for usage.", "error")
            sys.exit(1)

        # Route 3: Watch/Diff Snapshot Check
        if args.watch and not args.download_now:
            from reap.watcher import check_changes
            check_changes(args.url, args.output)
            return

        # Route 4: Core Engine Scraper
        from reap.engine import archive_site
        output_dir = archive_site(args.url, args.output, args.fast, args.threads)

        # Post-Processing Chain
        if args.clean:
            from reap.cleaner import clean_assets
            clean_assets(output_dir)

        if args.optimize:
            from reap.optimizer import optimize_assets
            optimize_assets(output_dir)

        if args.single_file:
            from reap.singlefile import bundle_to_single_file
            bundle_to_single_file(output_dir)

        if args.audit:
            from reap.audit import audit_directory
            audit_directory(output_dir)

        if args.deploy:
            from reap.deploy import deploy_to_netlify
            deploy_to_netlify(output_dir)

        if args.zip:
            from reap.utils import package_directory
            package_directory(output_dir)

        if args.serve:
            from reap.server import serve_directory
            serve_directory(output_dir, args.port)

    except KeyboardInterrupt:
        print_msg("\n\n[bold red]🌾 Harvest aborted by user. Cleaning up and exiting safely...[/bold red]", "interrupt")
        sys.exit(0)

if __name__ == "__main__":
    main()