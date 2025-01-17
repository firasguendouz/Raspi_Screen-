import subprocess
import time
from server.qr_code import generate_wifi_qr
import webview
import os
import base64

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
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                    background-color: #f4f4f9;
                    color: #333;
                    max-width: 1000px;
                    margin: 0 auto;
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                .header {
                    text-align: center;
                    padding: 20px;
                    background: #fff;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                #log {
                    white-space: pre-wrap;
                    font-family: monospace;
                    font-size: 1.1em;
                    background: #fff;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    height: 300px;
                    overflow-y: auto;
                    box-shadow: inset 0 0 5px rgba(0,0,0,0.1);
                }
                #status {
                    margin: 20px 0;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    transition: all 0.3s ease;
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
                    background: linear-gradient(90deg, #4CAF50, #45a049);
                    border-radius: 10px;
                    transition: width 0.3s ease;
                }
                .qr-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 20px;
                    flex-wrap: wrap;
                    margin: 20px 0;
                }
                .qr-code {
                    text-align: center;
                    background: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    max-width: 300px;
                    margin: 10px;
                }
                .qr-code img {
                    max-width: 250px;
                    height: auto;
                    margin: 10px auto;
                    border-radius: 10px;
                }
                .qr-code p {
                    margin: 10px 0;
                    font-weight: bold;
                    color: #666;
                }
                .status-pending { 
                    background-color: #fff3cd; 
                    color: #856404;
                    animation: pulse 2s infinite;
                }
                .status-success { 
                    background-color: #d4edda; 
                    color: #155724;
                }
                .status-error { 
                    background-color: #f8d7da; 
                    color: #721c24;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.8; }
                    100% { opacity: 1; }
                }
                .log-entry {
                    padding: 5px 0;
                    border-bottom: 1px solid #eee;
                }
                .log-time {
                    color: #666;
                    font-size: 0.9em;
                }
                .debug { color: #666; }
                .info { color: #0066cc; }
                .success { color: #28a745; }
                .error { color: #dc3545; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Raspberry Pi Setup</h1>
                    <div id="status"></div>
                    <div class="progress-container" id="progress-container">
                        <div class="progress-bar" id="progress-bar"></div>
                    </div>
                </div>
                <div class="qr-container" id="qr-container"></div>
                <div id="log"></div>
            </div>
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

    def log_message(self, message, level="info"):
        """Enhanced logging with timestamp and styling"""
        if self.window:
            timestamp = time.strftime("%H:%M:%S")
            safe_message = message.replace('"', '\\"').replace('\n', '\\n')
            
            script = f'''
            const log = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'log-entry {level}';
            entry.innerHTML = `<span class="log-time">[{timestamp}]</span> {safe_message}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
            '''
            
            self.window.evaluate_js(script)

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

    def image_to_data_url(self, image_path):
        """Convert image to base64 data URL"""
        try:
            with open(image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                return f'data:image/png;base64,{img_data}'
        except Exception as e:
            print(f"Error converting image to data URL: {e}")
            return None

    def display_qr_code(self, image_path, message=None):
        """Display QR code using data URL approach"""
        if self.window:
            try:
                # Convert image to data URL
                data_url = self.image_to_data_url(image_path)
                if not data_url:
                    self.log_message("Failed to convert image to data URL", "error")
                    return

                script = f'''
                try {{
                    const container = document.getElementById('qr-container');
                    container.innerHTML = ''; // Clear existing
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'qr-code';
                    
                    if ("{message}") {{
                        const msg = document.createElement('p');
                        msg.textContent = "{message}";
                        wrapper.appendChild(msg);
                    }}
                    
                    const img = document.createElement('img');
                    img.onload = () => {{
                        console.log('QR code loaded successfully');
                        this.log_message('QR code displayed successfully', 'success');
                    }};
                    
                    img.onerror = (e) => {{
                        console.error('Failed to load QR:', e);
                        this.log_message('Failed to load QR code', 'error');
                    }};

                    img.src = "{data_url}";
                    img.alt = "QR Code";
                    
                    wrapper.appendChild(img);
                    container.appendChild(wrapper);
                }} catch(error) {{
                    console.error('Error:', error);
                    this.log_message('Error displaying QR code: ' + error, 'error');
                }}
                '''
                
                self.window.evaluate_js(script)
                self.log_message(f"Displaying QR code from: {image_path}", "info")
                
            except Exception as e:
                self.log_message(f"Error in display_qr_code: {e}", "error")

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
