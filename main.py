import os
import subprocess
import time
from multiprocessing import Process
from dotenv import load_dotenv
import webview
from colorama import Fore, Style, init
from typing import Optional

from ap.ap_manager import APManager
from ap.network_manager import NetworkManager
from server.activation_manager import ActivationManager
from server.qr_code import generate_url_qr, generate_wifi_qr
from ui_manager.ui_manager import UIManager
from server.app import app  # Flask app
from config.settings import get_config
from utils.error_handler import handle_errors, SetupError, NetworkError

# Initialize colorama for colored console output
init(autoreset=True)

class SetupManager:
    """
    Orchestrates the Raspberry Pi setup process using specialized managers for each responsibility.
    Uses dependency injection for better testability and flexibility.
    """
    def __init__(
        self,
        network_manager: Optional[NetworkManager] = None,
        ap_manager: Optional[APManager] = None,
        activation_manager: Optional[ActivationManager] = None,
        ui_manager: Optional[UIManager] = None,
        config: Optional[dict] = None
    ):
        self.config = config or get_config()
        self.network_manager = network_manager or NetworkManager()
        self.ap_manager = ap_manager or APManager()
        self.activation_manager = activation_manager or ActivationManager(
            server_url=self.config["server"]["url"]
        )
        self.ui_manager = ui_manager or UIManager()

    def log(self, message: str, image_path: str = None) -> None:
        """Log messages to console and UI."""
        print(Fore.CYAN + message + Style.RESET_ALL)
        self.ui_manager.update_ui(message, image_path)

    @handle_errors()
    def start_ap_mode(self) -> bool:
        """Start Access Point mode and handle QR code sequence."""
        self.log("Starting Access Point...")
        
        if not self.ap_manager.start_ap():
            raise SetupError("Failed to start Access Point")
            
        self.log("Access Point started successfully")
        
        # Generate and display WiFi QR code
        self.log("Generating WiFi QR code...")
        wifi_qr = generate_wifi_qr(
            ssid=self.config["network"]["ap_ssid"],
            password=self.config["network"]["ap_password"],
            security="WPA",
            output_file=str(self.config["paths"]["wifi_qr"])
        )
        
        if not wifi_qr:
            raise SetupError("Failed to generate QR codes")
            
        self.log(f"QR code generated at: {wifi_qr}")
        self.ui_manager.display_qr_code(wifi_qr, "Scan this QR code to connect to Raspberry Pi AP")
        
        # Wait for client connection
        self.log("Waiting for client connection...")
        client_mac = self.ap_manager.wait_for_client_connection(
            timeout=self.config["timeouts"]["client_connection"]
        )
        
        if not client_mac:
            raise NetworkError("No client connected within timeout period")
            
        self.log(f"Client connected! MAC: {client_mac}")
        
        # Generate and display URL QR code
        self.log("Generating setup page QR code...")
        url = f"http://{self.config['network']['ap_ip']}"
        url_qr = generate_url_qr(url, str(self.config["paths"]["url_qr"]))
        
        if url_qr:
            self.log(f"Setup page QR code generated at: {url_qr}")
            self.ui_manager.display_qr_code(url_qr, "Scan to open WiFi setup page")
            return True
            
        return False

    @handle_errors()
    def stop_ap_mode(self) -> bool:
        """Stop Access Point mode and reset network configuration."""
        self.log("Stopping Access Point...")
        
        if not self.ap_manager.stop_ap():
            raise SetupError("Failed to stop Access Point")
            
        self.log("Access Point stopped.")
        
        # Reset DNS with multiple attempts
        max_attempts = self.config["timeouts"]["dns_reset_attempts"]
        delay = self.config["timeouts"]["dns_reset_delay"]
        
        for attempt in range(max_attempts):
            if self.network_manager.reset_dns():
                self.log("DNS reset successful")
                break
            else:
                self.log(f"DNS reset attempt {attempt + 1} failed, retrying...")
                time.sleep(delay)
        
        if not self.network_manager.verify_dns_config():
            raise NetworkError("DNS configuration may not be correct")
            
        return True

    @handle_errors()
    def handle_user_credentials(self) -> bool:
        """Handle WiFi credentials submission and connection."""
        flask_process = Process(target=self.start_flask_server)
        flask_process.start()
        
        # Wait for credentials file
        creds_file = self.config["paths"]["wifi_credentials_tmp"]
        while not os.path.exists(creds_file):
            time.sleep(2)
            
        # Read credentials
        with open(creds_file) as f:
            ssid = f.readline().strip()
            password = f.readline().strip()
            
        # Remove credentials file
        os.remove(creds_file)
        
        # Stop Flask server
        flask_process.terminate()
        flask_process.join()
        
        # Connect to WiFi
        return self.network_manager.connect_wifi(ssid, password)

    def start_flask_server(self) -> None:
        """Start Flask server for WiFi setup page."""
        app.run(
            host=self.config["server"]["host"],
            port=self.config["server"]["port"]
        )

@handle_errors()
def main():
    """Entry point for the Raspberry Pi setup process."""
    # Load environment variables
    load_dotenv()
    config = get_config()

    setup_manager = SetupManager(config=config)

    def webview_ready():
        """Orchestrate the setup process once webview is ready."""
        try:
            if setup_manager.network_manager.check_internet_connection():
                setup_manager.log("Device is already connected to the internet.")
                success, message = setup_manager.activation_manager.send_activation_request()
                if success:
                    setup_manager.log("Setup completed successfully. Exiting...")
                    setup_manager.ui_manager.close_ui()
                else:
                    raise SetupError(f"Activation failed: {message}")
            else:
                setup_manager.log("Device not connected. Starting Access Point mode...")
                if setup_manager.start_ap_mode():
                    if setup_manager.handle_user_credentials():
                        setup_manager.stop_ap_mode()
                        
                        if setup_manager.network_manager.check_internet_connection():
                            success, message = setup_manager.activation_manager.send_activation_request()
                            if success:
                                setup_manager.log("Setup completed successfully. Exiting...")
                                setup_manager.ui_manager.close_ui()
                                return
                            else:
                                raise SetupError(f"Activation failed: {message}")
                        
            setup_manager.log("Setup failed. Restarting process...")
            main()
        except Exception as e:
            setup_manager.log(f"Error during setup: {str(e)}")
            raise

    # Initialize PyWebView in the UIManager
    setup_manager.ui_manager.create_ui(webview_ready)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "Setup interrupted by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)



