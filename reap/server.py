import http.server
import socketserver
import os
from reap.utils import print_msg

def serve_directory(directory, port=8000):
    if not os.path.exists(directory):
        print_msg(f"Cannot serve: directory '{directory}' does not exist.", "error")
        return

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print_msg(f"\nLocal server online: http://localhost:{port}", "success")
            print_msg("Press Ctrl+C to terminate server session.", "info")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print_msg("\nServer stopped.", "info")