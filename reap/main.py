import sys
from reap.cli import parse_args
from reap.utils import print_msg, print_banner


def main():
    args = parse_args()

    from reap.utils import set_verbose
    set_verbose(args.verbose)

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
            print_msg("🌾 reap — web reconstruction engine", "info")
            print_msg("\nBasic Usage:", "info")
            print_msg("  reap https://example.com --mode app", "info")
            print_msg("\nFor full options, run 'reap --help' or 'reap --explore'", "info")
            sys.exit(1)

        # Route 3: Watch/Diff Snapshot Check
        if args.watch and not args.download_now:
            from reap.watcher import check_changes
            check_changes(args.url, args.output)
            return

        if args.verbose:
            print_banner()

        if args.verbose:
            # Route 4: Core Engine Scraper (v2)
            from reap.engine import archive_site
            output_dir, failed_urls = archive_site(
                args.url, args.output, args.mode, args.js, args.fast, args.threads
            )
        else:
            # SLEEK MODE UX
            import os
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()

            from rich.progress import (
                Progress,
                SpinnerColumn,
                TextColumn,
                TimeElapsedColumn,
            )
            from reap.utils import console
            from reap.engine import archive_site

            with Progress(
                SpinnerColumn("dots", style="gold3"),
                TextColumn("[bold gold3]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Crawling, Parsing & Downloading...", total=None
                )
                output_dir, failed_urls = archive_site(
                    args.url,
                    args.output,
                    args.mode,
                    args.js,
                    args.fast,
                    args.threads,
                    verbose=False,
                )

                # Post-Processing Chain
                if args.clean:
                    progress.update(task, description="Cleaning assets...")
                    from reap.cleaner import clean_assets
                    clean_assets(output_dir)

                if args.optimize:
                    progress.update(task, description="Optimizing assets...")
                    from reap.optimizer import optimize_assets
                    optimize_assets(output_dir)

                if args.single_file:
                    progress.update(task, description="Bundling to single file...")
                    from reap.singlefile import bundle_to_single_file
                    bundle_to_single_file(output_dir)

                if args.audit:
                    progress.update(task, description="Validating integrity...")
                    from reap.audit import audit_directory
                    audit_directory(output_dir)

                if args.deploy:
                    progress.update(task, description=f"Deploying ({args.deploy})...")
                    from reap.deploy import deploy
                    deploy(args.deploy, output_dir, args.url)

                if args.zip:
                    progress.update(task, description="Packaging archive...")
                    from reap.utils import package_directory
                    package_directory(output_dir)

                if args.serve:
                    progress.stop()
                    from reap.server import serve_directory
                    serve_directory(output_dir, args.port)

                progress.update(
                    task,
                    description="[bold green]✔ Pipeline Complete[/bold green]",
                )

        if not args.verbose and not args.serve:
            print_msg("\n✔ Done", "success")

        if failed_urls:
            print_msg(
                f"\n⚠️ Encountered {len(failed_urls)} failed asset/page downloads during build:",
                "warning",
            )
            for url in list(set(failed_urls))[:10]:
                print_msg(f"  - {url}", "warning")
            if len(set(failed_urls)) > 10:
                print_msg(
                    f"  ... and {len(set(failed_urls)) - 10} more.", "warning"
                )

    except KeyboardInterrupt:
        print_msg(
            "\n\n[bold red]🌾 Harvest aborted by user. Cleaning up and exiting safely...[/bold red]",
            "interrupt",
        )
        sys.exit(0)


if __name__ == "__main__":
    main()