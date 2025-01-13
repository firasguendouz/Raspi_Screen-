import os
import subprocess
import time
from multiprocessing import Process
from colorama import Fore, Style, init
from dotenv import load_dotenv
from server.wifi_config import WiFiConfig
from server.qr_code import generate_wifi_qr
from scripts.connect_wifi import connect_wifi
from scripts.send_activation import ActivationClient
from server.app import app  # Import the Flask app

# Initialize colorama for colored console output
init(autoreset=True)

class SetupManager:
    def __init__(self, server_url):
        self.wifi_config = WiFiConfig()
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

    def monitor_ap_connections(self):
        """Monitor devices connected to the Access Point."""
        try:
            self.log("Monitoring devices connected to the Access Point...", "info")
            while True:
                # Use arp-scan or similar tool to list connected devices
                result = subprocess.run(['sudo', 'arp-scan', '--interface=wlan0', '--localnet'], 
                                        capture_output=True, text=True)
                connected_devices = []
                for line in result.stdout.split('\n'):
                    if "MAC Address" not in line and line.strip():
                        connected_devices.append(line)

                if connected_devices:
                    self.log(f"Devices connected: {len(connected_devices)}", "success")
                    for device in connected_devices:
                        self.log(f"Device details: {device}", "info")
                else:
                    self.log("No devices currently connected.", "warning")

                time.sleep(10)
        except Exception as e:
            self.log(f"Error monitoring AP connections: {e}", "error")

    def stop_ap_mode(self):
        """Stop Access Point mode and reset DNS."""
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            self.reset_dns()
            self.log("Access Point mode stopped successfully and DNS reset.", "success")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to stop Access Point mode: {e}", "error")
            return False

    def check_internet_connection(self):
        """Check if the device has internet connectivity."""
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            self.log("Internet connection detected.", "success")
            return True
        except subprocess.CalledProcessError:
            self.log("No internet connection detected.", "warning")
            return False

    def setup_wifi(self, ssid, password):
        """Configure Wi-Fi connection and reset DNS."""
        if connect_wifi(ssid, password):
            self.reset_dns()
            self.log(f"Successfully connected to Wi-Fi network: {ssid}", "success")
            return True
        self.log(f"Failed to connect to Wi-Fi network: {ssid}", "error")
        return False

    def reset_dns(self):
        """Reset DNS configuration to Google's public DNS servers."""
        try:
            with open('/etc/resolv.conf', 'w') as resolv_file:
                resolv_file.write("nameserver 8.8.8.8\n")
                resolv_file.write("nameserver 8.8.4.4\n")
            self.log("DNS configuration reset successfully.", "success")
        except Exception as e:
            self.log(f"Failed to reset DNS configuration: {e}", "error")

    def activate_device(self):
        """Send activation request to the central server."""
        success, result = self.activation_client.send_activation_request()
        if success:
            self.log("Device activated successfully.", "success")
        else:
            self.log(f"Activation failed: {result}", "error")
        return success, result

    def start_streaming(self, url):
        """Start streaming mode."""
        try:
            subprocess.Popen(['python3', 'scripts/stream_url.py', url])
            self.log(f"Streaming started at URL: {url}", "success")
            return True
        except Exception as e:
            self.log(f"Failed to start streaming: {e}", "error")
            return False

def start_flask_server():
    """Start the Flask server."""
    app.run(host="0.0.0.0", port=80)

def main():
    # Load environment variables from .env
    load_dotenv()

    # Retrieve the server URL from the .env file
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")

    # Start the Flask server in a separate process
    flask_process = Process(target=start_flask_server)
    flask_process.start()

    setup_manager = SetupManager(server_url=SERVER_URL)

    # Check if the device is already connected to the internet
    if not setup_manager.check_internet_connection():
        setup_manager.log("No internet connection detected. Starting Access Point mode...", "warning")

        # Start AP mode
        if not setup_manager.start_ap_mode():
            setup_manager.log("Failed to start Access Point mode.", "error")
            flask_process.terminate()
            return

        # Start monitoring AP connections in a separate process
        ap_monitor_process = Process(target=setup_manager.monitor_ap_connections)
        ap_monitor_process.start()

        # Generate and display QR code for AP credentials
        generate_wifi_qr("RaspberryAP", "raspberry")
        setup_manager.log("QR code for Access Point credentials generated.", "info")

        # Wait for Wi-Fi configuration via web server
        setup_manager.log("Waiting for Wi-Fi configuration...", "info")
        while not setup_manager.check_internet_connection():
            time.sleep(10)

        # Stop AP mode once connected to the internet
        setup_manager.stop_ap_mode()
        ap_monitor_process.terminate()

    setup_manager.log("Internet connection established.", "success")

    # Attempt to activate the device
    setup_manager.log("Activating device...", "info")
    success, result = setup_manager.activate_device()

    if success:
        # Start streaming if a URL is provided in the activation response
        if isinstance(result, dict) and 'stream_url' in result:
            setup_manager.start_streaming(result['stream_url'])
        else:
            setup_manager.log("No streaming URL provided.", "warning")
    else:
        setup_manager.log(f"Activation failed: {result}", "error")

    # Ensure Flask server continues running
    flask_process.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nSetup interrupted by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
