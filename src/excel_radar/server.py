"""Simple HTTP server for previewing the radar locally."""

import http.server
import socketserver
import webbrowser
from pathlib import Path
from typing import Optional


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with minimal logging."""

    def log_message(self, format: str, *args: any) -> None:
        """Override to reduce logging noise."""
        # Only log errors
        if args[1] != "200":
            super().log_message(format, *args)


def serve_directory(
    directory: Path,
    port: int = 5173,
    open_browser: bool = True,
    host: str = "localhost",
) -> None:
    """
    Start a simple HTTP server to preview the radar.
    
    Args:
        directory: Directory to serve (usually dist/)
        port: Port to serve on
        open_browser: Whether to open browser automatically
        host: Host to bind to
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    # Change to the directory
    import os
    original_dir = os.getcwd()
    os.chdir(directory)
    
    try:
        with socketserver.TCPServer((host, port), QuietHTTPRequestHandler) as httpd:
            url = f"http://{host}:{port}"
            print(f"🚀 Serving radar at: {url}")
            print(f"📁 Directory: {directory.absolute()}")
            print("Press Ctrl+C to stop")
            
            if open_browser:
                webbrowser.open(url)
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port with --port")
        else:
            raise
    finally:
        os.chdir(original_dir)

# Made with Bob
