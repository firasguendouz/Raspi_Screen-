import os
import subprocess
import time
from multiprocessing import Process
import webview
from colorama import Fore, Style, init
from dotenv import load_dotenv
from server.qr_code import generate_wifi_qr
from scripts.connect_wifi import connect_wifi
from scripts.send_activation import ActivationClient
from server.app import app  # Flask app

# Initialize colorama
init(autoreset=True)


class SetupManager:
    def __init__(self, server_url):
        self.activation_client = ActivationClient(server_url=server_url)
        self.window = None  # To hold the pywebview window reference

    def log(self, message, image_path=None):
        """Log message to console and update UI."""
        print(Fore.CYAN + message + Style.RESET_ALL)
        if self.window:
            # Add message to the log
            self.window.evaluate_js(f'document.getElementById("log").innerText += "{message}\\n";')
            # If image is provided, display it
            if image_path:
                self.window.evaluate_js(f'''
                    const img = document.getElementById('qr-code');
                    if (!img) {{
                        const newImg = document.createElement('img');
                        newImg.id = 'qr-code';
                        newImg.src = 'file://{image_path}';
                        newImg.style = 'display:block; margin:20px auto; max-width:80%;';
                        document.body.appendChild(newImg);
                    }}
                ''')


    def start_ap_mode(self):
        """Start Access Point mode."""
        self.log("Starting Access Point...")
        try:
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            self.log("Access Point started. Generating QR code...")
            qr_path = generate_wifi_qr("RaspberryAP", "raspberry")
            self.log("QR code generated. Ready to connect.", image_path=qr_path)
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to start Access Point: {e}")


    def stop_ap_mode(self):
        """Stop Access Point mode."""
        self.log("Stopping Access Point...")
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            self.log("Access Point stopped.")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to stop Access Point: {e}")

    def check_internet_connection(self):
        """Check if the device has internet connectivity."""
        self.log("Checking internet connection...")
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            self.log("Internet connected.")
            return True
        except subprocess.CalledProcessError:
            self.log("No internet connection detected.")
            return False

    def activate_device(self):
        """Send activation request to the central server."""
        self.log("Sending activation request...")
        success, result = self.activation_client.send_activation_request()
        if success:
            self.log("Activation successful!")
            return True
        else:
            self.log(f"Activation failed: {result}")
            return False

    def handle_user_credentials(self):
        """Handle the Flask server and process user credentials."""
        flask_process = Process(target=self.start_flask_server)
        flask_process.start()

        self.log("Waiting for user to submit credentials...")
        while not self.check_internet_connection():
            time.sleep(10)

        self.log("Stopping Flask server and Access Point...")
        flask_process.terminate()
        flask_process.join()
        self.stop_ap_mode()

    def start_flask_server(self):
        """Start the Flask server."""
        app.run(host="0.0.0.0", port=80)


def main():
    load_dotenv()
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")

    setup_manager = SetupManager(server_url=SERVER_URL)

    # HTML template for pywebview
    html_template = """
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
        </style>
    </head>
    <body>
        <h1>Raspberry Pi Setup</h1>
        <div id="log">Initializing...\n</div>
    </body>
    </html>
    """

    # Start pywebview UI
    def webview_ready():
        if setup_manager.check_internet_connection():
            setup_manager.log("Device is already connected to the internet.")
            if setup_manager.activate_device():
                setup_manager.log("Setup completed successfully. Exiting...")
                webview.destroy_window()
        else:
            setup_manager.log("Device not connected. Starting Access Point mode...")
            setup_manager.start_ap_mode()
            setup_manager.handle_user_credentials()
            if setup_manager.check_internet_connection():
                if setup_manager.activate_device():
                    setup_manager.log("Setup completed successfully. Exiting...")
                else:
                    setup_manager.log("Activation failed. Please try again.")
            else:
                setup_manager.log("Failed to connect. Restarting process...")
                main()

    # Create the pywebview window in fullscreen
    window = webview.create_window("Raspberry Pi Setup", html=html_template, fullscreen=True)
    setup_manager.window = window  # Store the window reference
    webview.start(webview_ready, debug=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "Setup interrupted by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
