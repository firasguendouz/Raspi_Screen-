import os
import subprocess
import time
from multiprocessing import Process
from dotenv import load_dotenv
import webview
from colorama import Fore, Style, init
from server.qr_code import generate_wifi_qr
from scripts.connect_wifi import connect_wifi
from scripts.send_activation import ActivationClient
from server.app import app  # Flask app
from ui_manager.ui_manager import UIManager

# Initialize colorama for colored console output
init(autoreset=True)

class SetupManager:
    """
    Manages the Raspberry Pi setup process, including network configuration, 
    Access Point (AP) mode, and device activation.
    """
    def __init__(self, server_url):
        self.activation_client = ActivationClient(server_url=server_url)
        self.ui_manager = UIManager()  # Instantiate the UIManager

    def log(self, message, image_path=None):
        """
        Logs messages to the console and updates the PyWebView UI.

        :param message: The message to log.
        :param image_path: Optional image path to display in the UI.
        """
        print(Fore.CYAN + message + Style.RESET_ALL)
        self.ui_manager.update_ui(message, image_path)

    def start_ap_mode(self):
        """
        Starts the Raspberry Pi in Access Point mode and generates a QR code 
        for connecting to the AP.
        """
        self.log("Starting Access Point...")
        try:
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            self.log("Access Point started. Generating QR code...")
            qr_path = generate_wifi_qr("RaspberryAP", "raspberry")
            self.log("QR code generated. Ready to connect.", image_path=qr_path)
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to start Access Point: {e}")

    def stop_ap_mode(self):
        """
        Stops the Access Point mode.
        """
        self.log("Stopping Access Point...")
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            self.log("Access Point stopped.")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to stop Access Point: {e}")

    def check_internet_connection(self):
        """
        Checks if the Raspberry Pi is connected to the internet by pinging 
        Google's public DNS server.

        :return: True if connected, False otherwise.
        """
        self.log("Checking internet connection...")
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            self.log("Internet connected.")
            return True
        except subprocess.CalledProcessError:
            self.log("No internet connection detected.")
            return False

    def activate_device(self):
        """
        Sends an activation request to the central server.

        :return: True if activation succeeds, False otherwise.
        """
        self.log("Sending activation request...")
        success, result = self.activation_client.send_activation_request()
        if success:
            self.log("Activation successful!")
            return True
        else:
            self.log(f"Activation failed: {result}")
            return False

    def handle_user_credentials(self):
        """
        Starts the Flask server to accept user credentials and attempts to 
        connect to the provided Wi-Fi network.
        """
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
        """
        Starts the Flask web server for Wi-Fi credential submission.
        """
        app.run(host="0.0.0.0", port=80)


def main():
    """
    Entry point for the Raspberry Pi setup process.
    """
    # Load environment variables
    load_dotenv()
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")

    setup_manager = SetupManager(server_url=SERVER_URL)

    def webview_ready():
        """
        Callback for PyWebView, orchestrates the setup process.
        """
        if setup_manager.check_internet_connection():
            setup_manager.log("Device is already connected to the internet.")
            if setup_manager.activate_device():
                setup_manager.log("Setup completed successfully. Exiting...")
                setup_manager.ui_manager.close_ui()
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

    # Initialize PyWebView in the UIManager
    setup_manager.ui_manager.create_ui(webview_ready)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "Setup interrupted by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
