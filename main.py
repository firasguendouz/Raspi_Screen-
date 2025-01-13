import os
import subprocess
import time
from multiprocessing import Process
from colorama import Fore, Style, init
from dotenv import load_dotenv
from server.app import app  # Import the Flask app
from server.qr_code import generate_wifi_qr
from scripts.send_activation import ActivationClient

# Initialize colorama for colored console output
init(autoreset=True)

class SetupManager:
    def __init__(self, server_url):
        self.activation_client = ActivationClient(server_url=server_url)

    def log(self, message, level="info"):
        """Enhanced logging with colors based on log level."""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
        }
        print(f"{colors.get(level, Fore.WHITE)}{message}{Style.RESET_ALL}")

    def start_ap_mode(self):
        """Initialize Access Point mode."""
        try:
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            self.log("Access Point mode started successfully.", "success")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to start Access Point mode: {e}", "error")
            return False

    def stop_ap_mode(self):
        """Stop Access Point mode."""
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            self.log("Access Point mode stopped successfully.", "success")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to stop Access Point mode: {e}", "error")
            return False

    def check_internet_connection(self):
        """Check internet connectivity."""
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            self.log("Internet connection detected.", "success")
            return True
        except subprocess.CalledProcessError:
            self.log("No internet connection detected.", "warning")
            return False

    def activate_device(self):
        """Send activation request to the central server."""
        success, result = self.activation_client.send_activation_request()
        if success:
            self.log("Device activated successfully.", "success")
        else:
            self.log(f"Activation failed: {result}", "error")
        return success, result


def start_flask_server():
    """Start the Flask server."""
    app.run(host="0.0.0.0", port=80)

def main():
    load_dotenv()
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")

    setup_manager = SetupManager(server_url=SERVER_URL)

    if not setup_manager.check_internet_connection():
        setup_manager.log("No internet connection detected. Starting Access Point mode...", "warning")
        if not setup_manager.start_ap_mode():
            return

        # Start Flask server for credentials
        flask_process = Process(target=start_flask_server)
        flask_process.start()

        setup_manager.log("Waiting for Wi-Fi credentials...", "info")
        while not setup_manager.check_internet_connection():
            time.sleep(10)

        # Stop AP mode and Flask server after connection
        setup_manager.stop_ap_mode()
        flask_process.terminate()
        flask_process.join()

    setup_manager.log("Internet connection established. Activating device...", "info")
    success, result = setup_manager.activate_device()

    if success:
        setup_manager.log("Setup completed successfully.", "success")
    else:
        setup_manager.log("Setup failed during activation.", "error")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "Setup interrupted by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
