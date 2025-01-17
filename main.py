import os
import subprocess
import time
from multiprocessing import Process
from dotenv import load_dotenv
import webview
from colorama import Fore, Style, init
from server.qr_code import generate_url_qr, generate_wifi_qr
from scripts.connect_wifi import connect_wifi
from scripts.connect_wifi import reset_dns

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
        """Starts the Raspberry Pi in Access Point mode and handles QR code sequence"""
        self.log("Starting Access Point...")
        try:
            # Start AP
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            self.log("Access Point started successfully")
            
            # Generate and display WiFi QR code
            self.log("Generating WiFi QR code...")
            wifi_qr = generate_wifi_qr("RaspberryAP", "raspberry", "wifi_qr.png")
            
            if wifi_qr:
                self.log(f"QR code generated at: {wifi_qr}")
                self.ui_manager.display_qr_code(
                    wifi_qr,
                    "Scan this QR code to connect to Raspberry Pi AP"
                )
                self.log("Waiting for client connection...")
                
                # Monitor for client connection
                while True:
                    try:
                        connected_device = subprocess.check_output(
                            ['iw', 'dev', 'wlan0', 'station', 'dump']
                        ).decode()
                        
                        if connected_device:
                            client_mac = connected_device.split('\n')[0].split()[1]
                            self.log(f"Client connected! MAC: {client_mac}")
                            
                            # Generate and display URL QR code
                            self.log("Generating setup page QR code...")
                            url_qr = generate_url_qr(
                                "http://192.168.4.1",
                                "web_qr.png"
                            )
                            
                            if url_qr:
                                self.log(f"Setup page QR code generated at: {url_qr}")
                                self.ui_manager.display_qr_code(
                                    url_qr,
                                    "Scan to open WiFi setup page"
                                )
                            break
                        
                        time.sleep(2)
                        
                    except subprocess.CalledProcessError as e:
                        self.log(f"Error checking connection: {e}", "error")
                        continue
                        
            else:
                self.log("Failed to generate QR codes", "error")
                
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to start Access Point: {e}", "error")

    def stop_ap_mode(self):
        """
        Stops the Access Point mode and ensures DNS is properly reset.
        """
        self.log("Stopping Access Point...")
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            self.log("Access Point stopped.")
            
            # Add multiple DNS reset attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                if reset_dns():
                    self.log("DNS reset successful")
                    break
                else:
                    self.log(f"DNS reset attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
            
            # Final verification
            if not self.verify_dns_config():
                self.log("Warning: DNS configuration may not be correct", "warning")
                
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to stop Access Point: {e}")

    def verify_dns_config(self):
        """
        Verify DNS configuration is correct.
        """
        try:
            with open('/etc/resolv.conf', 'r') as f:
                content = f.read()
                return '8.8.8.8' in content and '8.8.4.4' in content
        except:
            return False

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
        
        # Wait for credentials file
        creds_file = 'wifi_credentials.tmp'
        while not os.path.exists(creds_file):
            time.sleep(2)
            
        
        
        # Remove credentials file
        #os.remove(creds_file)
        # Stop Flask server
        flask_process.terminate()
        flask_process.join()
        return True
        

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
            # Log client connection and display redirect message
            connected_device = subprocess.check_output(['iw', 'dev', 'wlan0', 'station', 'dump']).decode()
            if connected_device:
                setup_manager.log("Client device connected!")
                client_mac = connected_device.split('\n')[0].split()[1]
                setup_manager.log(f"Client MAC: {client_mac}")
                
                # Generate QR code for flask web interface
                redirect_url = "http://192.168.4.1"
                web_qr_path = generate_wifi_qr(redirect_url, "", output_file="web_qr.png")
                if web_qr_path:
                    setup_manager.log("Scan QR code to access setup page:", web_qr_path)
            if setup_manager.handle_user_credentials() :
                setup_manager.stop_ap_mode()
                # Read credentials
                creds_file = 'wifi_credentials.tmp'
                with open(creds_file) as f:
                    ssid = f.readline().strip()
                    password = f.readline().strip()
                connect_wifi(ssid, password)
                reset_dns()

                # Remove credentials file
                os.remove(creds_file)       
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



