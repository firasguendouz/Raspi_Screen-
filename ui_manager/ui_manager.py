import subprocess
import time
from server.qr_code import generate_wifi_qr
import webview

class UIManager:
    """
    Manages the PyWebView interface for the Raspberry Pi setup application.
    """

    def __init__(self):
        """Initialize the UIManager with an enhanced HTML template."""
        self.window = None
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Raspberry Pi Setup</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: #f4f4f9;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                }
                #log {
                    white-space: pre-wrap;
                    font-size: 1.2em;
                    background: #fff;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    height: 400px;
                    overflow-y: auto;
                }
                #status {
                    margin: 20px 0;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                }
                .progress-container {
                    width: 100%;
                    background-color: #f0f0f0;
                    border-radius: 10px;
                    margin: 10px 0;
                    display: none;
                }
                .progress-bar {
                    width: 0%;
                    height: 20px;
                    background-color: #4CAF50;
                    border-radius: 10px;
                    transition: width 0.3s ease;
                }
                img {
                    display: block;
                    margin: 20px auto;
                    max-width: 300px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                .status-pending { background-color: #fff3cd; color: #856404; }
                .status-success { background-color: #d4edda; color: #155724; }
                .status-error { background-color: #f8d7da; color: #721c24; }
            </style>
        </head>
        <body>
            <h1>Raspberry Pi Setup</h1>
            <div id="status"></div>
            <div class="progress-container" id="progress-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
            <div id="log">Initializing...\n</div>
        </body>
        </html>
        """

    def create_ui(self, ready_callback):
        """
        Creates and starts the PyWebView UI with error handling.
        
        Args:
            ready_callback (function): Function to execute when the UI is ready.
        """
        try:
            self.create_window()
            self.start_ui(ready_callback)
        except Exception as e:
            print(f"Failed to create UI: {e}")
            # Attempt to recreate window once
            try:
                self.window = None
                self.create_window()
                self.start_ui(ready_callback)
            except Exception as e:
                print(f"Fatal error creating UI: {e}")
                raise

    def update_ui(self, message, image_path=None, max_retries=3):
        """
        Updates the UI with new messages and images with retry mechanism.
        
        Args:
            message (str): The message to display
            image_path (str, optional): Path to an image to display
            max_retries (int): Maximum number of retry attempts
        """
        retries = 0
        while retries < max_retries:
            try:
                self.log_message(message, image_path)
                return
            except Exception as e:
                retries += 1
                print(f"Update UI failed (attempt {retries}/{max_retries}): {e}")
                time.sleep(1)  # Wait before retry
        
        print("Failed to update UI after maximum retries")

    def close_ui(self):
        """
        Closes the PyWebView window safely.
        """
        if self.window:
            try:
                self.window.destroy()
            except Exception as e:
                print(f"Error closing window: {e}")
            finally:
                self.window = None

    def create_window(self):
        """
        Create the PyWebView window using the HTML template with error handling.
        """
        try:
            self.window = webview.create_window(
                "Raspberry Pi Setup",
                html=self.html_template,
                fullscreen=True
            )
        except Exception as e:
            print(f"Error creating window: {e}")
            # Try creating window in non-fullscreen mode as fallback
            try:
                self.window = webview.create_window(
                    "Raspberry Pi Setup",
                    html=self.html_template,
                    fullscreen=False,
                    width=800,
                    height=600
                )
            except Exception as e:
                print(f"Fatal error creating window: {e}")
                raise

    def update_status(self, message, status_type="pending"):
        """
        Update the status display with different styles.
        
        Args:
            message (str): Status message to display
            status_type (str): Type of status ('pending', 'success', or 'error')
        """
        if self.window:
            script = f'''
            const status = document.getElementById('status');
            status.innerText = "{message}";
            status.className = "status-{status_type}";
            '''
            self.window.evaluate_js(script)

    def update_progress(self, progress, show=True):
        """
        Update the progress bar.
        
        Args:
            progress (int): Progress percentage (0-100)
            show (bool): Whether to show or hide the progress bar
        """
        if self.window:
            script = f'''
            const container = document.getElementById('progress-container');
            const bar = document.getElementById('progress-bar');
            container.style.display = '{"block" if show else "none"}';
            bar.style.width = '{progress}%';
            '''
            self.window.evaluate_js(script)

    def log_message(self, message, image_path=None):
        """
        Enhanced log message with automatic status updates.
        
        Args:
            message (str): The message to log
            image_path (str, optional): Path to an image to display
        """
        if self.window:
            # Update status and progress based on message content
            if "Error" in message or "Failed" in message:
                self.update_status(message, "error")
            elif "Success" in message or "Complete" in message:
                self.update_status(message, "success")
            else:
                self.update_status(message, "pending")

            # Add message to log
            safe_message = message.replace('"', '\\"').replace('\n', '\\n')
            self.window.evaluate_js(f'document.getElementById("log").innerText += "{safe_message}\\n";')
            
            # Handle image display
            if image_path:
                self.window.evaluate_js(f'''
                    const existingImg = document.getElementById('qr-code');
                    if (!existingImg) {{
                        const img = document.createElement('img');
                        img.id = 'qr-code';
                        img.src = 'file://{image_path}';
                        document.body.appendChild(img);
                    }}
                ''')

    def destroy_window(self):
        """
        Destroy the PyWebView window and exit the application gracefully.
        """
        if self.window:
            self.window.destroy()

    def start_ui(self, ready_callback):
        """
        Start the PyWebView UI with a callback for setup logic.

        Args:
            ready_callback (function): Function to execute when the UI is ready.
        """
        webview.start(ready_callback, debug=False)

    def display_qr_code(self, image_path):
        """
        Display QR code in the UI window.
        
        Args:
            image_path (str): Path to QR code image
        """
        if self.window:
            script = f'''
            const content = document.getElementById('log');
            content.innerHTML += '<p>Access Point is ready. Scan QR code to connect:</p>';
            const img = document.createElement('img');
            img.src = 'file://{image_path}';
            img.id = 'wifi-qr';
            img.style.maxWidth = '300px';
            content.appendChild(img);
            '''
            self.window.evaluate_js(script)

    def start_ap_mode(self):
        """Starts the Raspberry Pi in Access Point mode with progress updates."""
        self.log("Starting Access Point...")
        self.update_progress(0, True)
        
        try:
            # Start AP
            self.update_progress(30)
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            self.update_progress(60)
            
            # Generate and display QR code
            qr_path = generate_wifi_qr("RaspberryAP", "raspberry")
            if qr_path:
                self.update_progress(90)
                self.display_qr_code(qr_path)
                self.log("Access Point ready. Please scan the QR code to connect.")
                self.update_progress(100)
                time.sleep(1)  # Show completed progress briefly
                self.update_progress(0, False)  # Hide progress bar
            else:
                self.log("Failed to generate QR code")
                self.update_status("QR Code Generation Failed", "error")
                
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to start Access Point: {e}")
            self.update_status("Access Point Setup Failed", "error")
