import os
import shutil
import urllib.request
import json
from reap.utils import print_msg

CONFIG_FILE = os.path.expanduser("~/.reap_config")

def get_access_token():
    """Gets or prompts the user for their Netlify Personal Access Token."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("netlify_token")
        except Exception:
            pass

    print_msg("\nDeploying to Netlify requires a Personal Access Token.", "warning")
    print_msg("Get one here: https://app.netlify.com/user/settings/applications (under Personal access tokens)", "info")
    
    token = input("Enter your Netlify Token: ").strip()
    if token:
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"netlify_token": token}, f)
        except Exception as e:
            print_msg(f"Could not save config file: {e}", "warning")
    return token

def deploy_to_netlify(directory):
    """Packages the directory as a zip and uploads it straight to Netlify's deployment servers."""
    token = get_access_token()
    if not token:
        print_msg("Deployment cancelled: Missing access token.", "error")
        return

    print_msg("Preparing assets for deployment...", "info")
    zip_temp_path = os.path.join(os.path.dirname(directory), "temp_deploy_package")
    
    try:
        # Create a temporary zip package
        shutil.make_archive(zip_temp_path, "zip", directory)
        zip_file = zip_temp_path + ".zip"
        
        with open(zip_file, "rb") as f:
            zip_data = f.read()
        
        print_msg("Uploading package to Netlify servers...", "info")
        
        # Deploy Request Configuration
        url = "https://api.netlify.com/api/v1/sites"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/zip",
        }
        
        req = urllib.request.Request(url, data=zip_data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            site_url = res_data.get("url")
            admin_url = res_data.get("admin_url")
            
            print_msg("\nDeployment Successful!", "success")
            print_msg(f"Live Production URL: [bold underline cyan]{site_url}[/bold underline cyan]", "success")
            print_msg(f"Admin Dashboard URL: {admin_url}", "info")
            
    except urllib.error.HTTPError as e:
        print_msg(f"Netlify API Rejected Request: Code {e.code} - {e.reason}", "error")
    except Exception as e:
        print_msg(f"Deployment failed: {e}", "error")
    finally:
        # Clean up temporary zip
        if os.path.exists(zip_temp_path + ".zip"):
            os.remove(zip_temp_path + ".zip")