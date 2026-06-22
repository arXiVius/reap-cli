import os
import subprocess
from urllib.parse import urlparse
from reap.utils import print_msg

def detect_best_provider(manifest_path):
    import json
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            mode = manifest.get('mode', 'app')
            if mode == 'app':
                return 'vercel' # SPA optimized
            elif len(manifest.get('routes', [])) > 100:
                return 'cf' # large distributed
    except Exception:
        pass
    return 'netlify'

def deploy_to_netlify(directory):
    print_msg("Deploying to Netlify...", "info")
    try:
        subprocess.run(["npx", "netlify", "deploy", "--prod", "--dir", directory], check=True)
        print_msg("Successfully deployed to Netlify!", "success")
    except subprocess.CalledProcessError:
        print_msg("Netlify deployment failed. Ensure you have the Netlify CLI installed and are logged in.", "error")

def deploy_to_vercel(directory):
    print_msg("Deploying to Vercel...", "info")
    try:
        subprocess.run(["npx", "vercel", "--prod", "--yes"], cwd=directory, check=True)
        print_msg("Successfully deployed to Vercel!", "success")
    except subprocess.CalledProcessError:
        print_msg("Vercel deployment failed. Ensure you have the Vercel CLI installed and are logged in.", "error")

def deploy_to_cloudflare(directory, project_name):
    print_msg("Deploying to Cloudflare Pages...", "info")
    try:
        subprocess.run(["npx", "wrangler", "pages", "deploy", directory, "--project-name", project_name], check=True)
        print_msg("Successfully deployed to Cloudflare Pages!", "success")
    except subprocess.CalledProcessError:
        print_msg("Cloudflare deployment failed. Ensure you have Wrangler installed and are logged in.", "error")

def deploy(provider, output_dir, start_url=None):
    if provider == "auto":
        manifest_path = os.path.join(output_dir, "manifest.json")
        provider = detect_best_provider(manifest_path)
        print_msg(f"Auto-detected best deployment provider: {provider.upper()}", "info")

    if provider == "vercel":
        deploy_to_vercel(output_dir)
    elif provider == "netlify":
        deploy_to_netlify(output_dir)
    elif provider in ("cf", "cloudflare"):
        project_name = "reap-" + (urlparse(start_url).netloc.replace(".", "-") if start_url else "site")
        deploy_to_cloudflare(output_dir, project_name)
    else:
        print_msg(f"Unknown deployment provider: {provider}", "error")