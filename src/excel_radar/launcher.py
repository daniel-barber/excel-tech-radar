"""
Radar Studio Launcher
Provides a GUI for selecting the data directory and launching the application.
"""
import sys
import os

# Set debug mode BEFORE any other imports to prevent secret key warning
# This is appropriate for standalone/desktop launcher (local use only)
os.environ.setdefault('RADAR_DEBUG', 'true')
os.environ.setdefault('RADAR_HOST', '127.0.0.1')

import json
import webbrowser
import threading
import time
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Import the server components
from excel_radar.config import Config


class RadarLauncher:
    """GUI launcher for Radar Studio."""
    
    def __init__(self):
        """Initialize the launcher."""
        self.root = tk.Tk()
        self.root.title("Radar Studio Launcher")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.center_window()
        
        # Configuration
        self.config_file = Path.home() / ".excel-radar" / "launcher.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        # State
        self.selected_directory: Optional[Path] = None
        self.server_thread: Optional[threading.Thread] = None
        self.server_running = False
        
        # Load last used directory
        self.load_config()
        
        # Build UI
        self.build_ui()
        
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_config(self):
        """Load the last used directory from config."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    last_dir = config.get('last_directory')
                    if last_dir and Path(last_dir).exists():
                        self.selected_directory = Path(last_dir)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save the selected directory to config."""
        try:
            config = {
                'last_directory': str(self.selected_directory) if self.selected_directory else None
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def build_ui(self):
        """Build the user interface."""
        # Header
        header_frame = tk.Frame(self.root, bg="#2196F3", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Radar Studio",
            font=("Arial", 24, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main content
        content_frame = tk.Frame(self.root, padx=40, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = tk.Label(
            content_frame,
            text="Select a directory to store your radar projects:",
            font=("Arial", 12),
            wraplength=500,
            justify=tk.LEFT
        )
        instructions.pack(pady=(0, 20))
        
        # Directory selection
        dir_frame = tk.Frame(content_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.dir_label = tk.Label(
            dir_frame,
            text=str(self.selected_directory) if self.selected_directory else "No directory selected",
            font=("Arial", 10),
            fg="#666",
            wraplength=400,
            justify=tk.LEFT
        )
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            dir_frame,
            text="Browse...",
            command=self.select_directory,
            font=("Arial", 11),
            padx=20,
            pady=6
        )
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="",
            font=("Arial", 10),
            fg="#4CAF50"
        )
        self.status_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=(20, 0))
        
        self.launch_btn = tk.Button(
            button_frame,
            text="Launch Radar",
            command=self.launch_server,
            font=("Arial", 12),
            padx=30,
            pady=10,
            state=tk.NORMAL if self.selected_directory else tk.DISABLED
        )
        self.launch_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="Stop Server",
            command=self.stop_server,
            font=("Arial", 12),
            padx=30,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = tk.Button(
            button_frame,
            text="Quit",
            command=self.quit_app,
            font=("Arial", 12),
            padx=30,
            pady=10
        )
        quit_btn.pack(side=tk.LEFT, padx=5)
        
        # Footer
        footer = tk.Label(
            content_frame,
            text="The server will run on http://localhost:8080",
            font=("Arial", 9),
            fg="#999"
        )
        footer.pack(side=tk.BOTTOM, pady=(20, 0))
    
    def select_directory(self):
        """Open directory selection dialog."""
        # Prevent changing directory while server is running
        if self.server_running:
            messagebox.showwarning(
                "Server Running",
                "Please stop the server before selecting a different directory."
            )
            return
        
        initial_dir = self.selected_directory if self.selected_directory else Path.home()
        
        directory = filedialog.askdirectory(
            title="Select Data Directory for Radar Studio",
            initialdir=initial_dir
        )
        
        if directory:
            self.selected_directory = Path(directory)
            self.dir_label.config(text=str(self.selected_directory))
            self.launch_btn.config(state=tk.NORMAL)
            self.save_config()
            self.status_label.config(text="Directory selected successfully", fg="#4CAF50")
    
    def launch_server(self):
        """Launch the radar server."""
        if not self.selected_directory:
            messagebox.showerror("Error", "Please select a directory first")
            return
        
        if self.server_running:
            messagebox.showinfo("Info", "Server is already running")
            return
        
        try:
            # Update UI
            self.status_label.config(text="Starting server...", fg="#2196F3")
            self.launch_btn.config(state=tk.DISABLED)
            self.root.update()
            
            # Set environment variable for data directory
            os.environ['RADAR_DATA_DIR'] = str(self.selected_directory)
            
            # Create data directory if it doesn't exist
            self.selected_directory.mkdir(exist_ok=True)
            
            # Start server in background thread
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Open browser
            webbrowser.open('http://localhost:8080')
            
            # Update UI
            self.server_running = True
            self.status_label.config(
                text="✓ Server running on http://localhost:8080",
                fg="#4CAF50"
            )
            self.stop_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server:\n{str(e)}")
            self.status_label.config(text="Failed to start server", fg="#f44336")
            self.launch_btn.config(state=tk.NORMAL)
    
    def run_server(self):
        """Run the Flask server (in background thread)."""
        try:
            # Set environment variables before loading config
            if self.selected_directory:
                data_dir = Path(self.selected_directory)
                os.environ['RADAR_DATA_DIR'] = str(data_dir)
                
                # Organize all app data under hidden .excel-radar subdirectory
                # This keeps the user's directory clean with only Excel files visible
                app_data_dir = data_dir / '.excel-radar'
                app_data_dir.mkdir(exist_ok=True)
                
                # Set writable directories inside .excel-radar
                # This prevents trying to write to the read-only bundle
                os.environ['RADAR_DIST_DIR'] = str(app_data_dir / 'exports')
                os.environ['RADAR_LOG_DIR'] = str(app_data_dir / 'logs')
                os.environ['RADAR_BACKUP_DIR'] = str(app_data_dir / 'backups')
                
                # Create subdirectories if they don't exist
                (app_data_dir / 'exports').mkdir(exist_ok=True)
                (app_data_dir / 'logs').mkdir(exist_ok=True)
                (app_data_dir / 'backups').mkdir(exist_ok=True)
            
            # For standalone launcher, use debug mode (local use only)
            # This prevents the secret key warning
            os.environ['RADAR_DEBUG'] = 'true'
            
            # Bind to localhost only for security
            os.environ['RADAR_HOST'] = '127.0.0.1'
            os.environ['RADAR_PORT'] = '8080'
            
            print(f"Starting server with data directory: {self.selected_directory}")
            print(f"Environment: DEBUG={os.environ.get('RADAR_DEBUG')}, HOST={os.environ.get('RADAR_HOST')}, PORT={os.environ.get('RADAR_PORT')}")
            print(f"Exports dir: {os.environ.get('RADAR_DIST_DIR')}, Logs dir: {os.environ.get('RADAR_LOG_DIR')}")
            
            # Load configuration (will use environment variables)
            from excel_radar.config import load_config
            config = load_config()
            
            print(f"Config loaded: host={config.host}, port={config.port}, data_dir={config.data_dir}")
            
            # Create and run app
            from excel_radar.api import RadarAPI
            api = RadarAPI(config)
            app = api.app
            
            print(f"Starting Flask server on {config.host}:{config.port}")
            
            # Run server
            app.run(
                host=config.host,
                port=config.port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            import traceback
            error_msg = f"Server error: {e}\n{traceback.format_exc()}"
            print(error_msg)
            self.server_running = False
            # Update UI on main thread
            self.root.after(0, lambda: self.status_label.config(
                text=f"Server failed: {str(e)[:50]}...",
                fg="#f44336"
            ))
            self.root.after(0, lambda: self.launch_btn.config(state=tk.NORMAL))
    
    def stop_server(self):
        """Stop the server."""
        if not self.server_running:
            return
        
        try:
            # Send shutdown request to Flask server
            import requests
            try:
                requests.post('http://localhost:8080/shutdown', timeout=2)
            except:
                pass  # Server might already be down
            
            # Update UI state
            self.server_running = False
            self.status_label.config(
                text="Server stopped. You can now select a different directory.",
                fg="#666"
            )
            self.launch_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            messagebox.showinfo(
                "Server Stopped",
                "The server has been stopped.\n"
                "You can now select a different directory and launch again."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server:\n{str(e)}")
    
    def quit_app(self):
        """Quit the application."""
        if self.server_running:
            response = messagebox.askyesno(
                "Confirm Quit",
                "The server is still running. Are you sure you want to quit?"
            )
            if not response:
                return
        
        self.root.quit()
        self.root.destroy()
        sys.exit(0)
    
    def run(self):
        """Run the launcher."""
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Start main loop
        self.root.mainloop()


def main():
    """Main entry point for the launcher."""
    try:
        launcher = RadarLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
