import hashlib
import os
from reap.utils import print_msg

def calculate_directory_hash(directory):
    """Calculates a unique SHA256 checksum for the structure and files of a directory."""
    hasher = hashlib.sha256()
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            # Skip logs or config metadata
            if file.endswith((".log", ".db")):
                continue
            hasher.update(file.encode("utf-8"))
            try:
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
            except IOError:
                pass
    return hasher.hexdigest()

def check_changes(url, directory):
    """Compares current target state structure hash with the previous save."""
    if not directory or not os.path.exists(directory):
        print_msg("Error: Output directory must exist to run change detection.", "error")
        return

    print_msg("Verifying site structure integrity...", "info")
    old_hash_file = os.path.join(directory, ".reap_hash")
    
    if not os.path.exists(old_hash_file):
        # Generate initial state
        current_hash = calculate_directory_hash(directory)
        with open(old_hash_file, "w") as f:
            f.write(current_hash)
        print_msg("Initial site tracking snapshot created.", "success")
        return

    with open(old_hash_file, "r") as f:
        stored_hash = f.read().strip()

    current_hash = calculate_directory_hash(directory)

    if stored_hash == current_hash:
        print_msg("Structure check completed. No modifications detected.", "success")
    else:
        print_msg("Alert: Structural alterations detected in the local copy vs snapshot.", "warning")
        print_msg("This can indicate modified static assets, design updates, or rewritten files.", "info")