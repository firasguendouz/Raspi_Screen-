import subprocess
import time
from server.wifi_config import WiFiConfig
from server.qr_code import generate_wifi_qr
from scripts.connect_wifi import connect_wifi
from scripts.send_activation import ActivationClient
from scripts.display_qr_code import generate_and_display_qr

class SetupManager:
    def __init__(self):
        self.wifi_config = WiFiConfig()
        self.activation_client = ActivationClient()

    def start_ap_mode(self):
        """Initialize Access Point mode."""
        try:
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            print("Access Point mode started successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start Access Point mode: {e}")
            return False

    def stop_ap_mode(self):
        """Stop Access Point mode."""
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            print("Access Point mode stopped successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop Access Point mode: {e}")
            return False

    def check_internet_connection(self):
        """Check if the device has internet connectivity."""
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def setup_wifi(self, ssid, password):
        """Configure Wi-Fi connection."""
        return connect_wifi(ssid, password)

    def activate_device(self):
        """Send activation request to the central server."""
        success, result = self.activation_client.send_activation_request()
        return success, result

    def start_streaming(self, url):
        """Start streaming mode."""
        try:
            subprocess.Popen(['python3', 'scripts/stream_url.py', url])
            return True
        except Exception as e:
            print(f"Failed to start streaming: {e}")
            return False

def main():
    setup_manager = SetupManager()

    # Check if the device is already connected to the internet
    if not setup_manager.check_internet_connection():
        print("No internet connection detected. Starting Access Point mode...")

        # Start AP mode
        if not setup_manager.start_ap_mode():
            print("Failed to start Access Point mode.")
            return

        # Generate and display QR code for AP credentials
        generate_and_display_qr("RaspberryAP", "raspberry")

        # Wait for Wi-Fi configuration via web server
        print("Waiting for Wi-Fi configuration...")
        while not setup_manager.check_internet_connection():
            time.sleep(10)

        # Stop AP mode once connected to the internet
        setup_manager.stop_ap_mode()

    print("Internet connection established.")

    # Attempt to activate the device
    print("Activating device...")
    success, result = setup_manager.activate_device()

    if success:
        print("Device activated successfully.")

        # Start streaming if a URL is provided in the activation response
        if isinstance(result, dict) and 'stream_url' in result:
            setup_manager.start_streaming(result['stream_url'])
        else:
            print("No streaming URL provided.")
    else:
        print(f"Activation failed: {result}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
