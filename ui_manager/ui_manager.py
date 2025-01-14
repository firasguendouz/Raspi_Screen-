import webview

class UIManager:
    """
    Manages the PyWebView interface for the Raspberry Pi setup application.
    """

    def __init__(self):
        """
        Initialize the UIManager with a default HTML template and a reference to the webview window.
        """
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
                img {
                    display: block;
                    margin: 20px auto;
                    max-width: 80%;
                }
            </style>
        </head>
        <body>
            <h1>Raspberry Pi Setup</h1>
            <div id="log">Initializing...\n</div>
        </body>
        </html>
        """

    def create_ui(self, ready_callback):
        """
        Creates and starts the PyWebView UI.
        
        Args:
            ready_callback (function): Function to execute when the UI is ready.
        """
        self.create_window()
        self.start_ui(ready_callback)

    def update_ui(self, message, image_path=None):
        """
        Updates the UI with new messages and images.
        
        Args:
            message (str): The message to display
            image_path (str, optional): Path to an image to display
        """
        self.log_message(message, image_path)

    def close_ui(self):
        """
        Closes the PyWebView window.
        """
        self.destroy_window()

    def create_window(self):
        """
        Create the PyWebView window using the HTML template.
        """
        self.window = webview.create_window("Raspberry Pi Setup", html=self.html_template, fullscreen=True)

    def log_message(self, message, image_path=None):
        """
        Log a message to the PyWebView UI and optionally display an image (e.g., QR code).

        Args:
            message (str): The message to log.
            image_path (str, optional): Path to an image to display in the UI.
        """
        if self.window:
            # Add message to the log
            self.window.evaluate_js(f'document.getElementById("log").innerText += "{message}\\n";')

            # If an image is provided, display it
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
            webview.destroy_window()

    def start_ui(self, ready_callback):
        """
        Start the PyWebView UI with a callback for setup logic.

        Args:
            ready_callback (function): Function to execute when the UI is ready.
        """
        webview.start(ready_callback, debug=False)
