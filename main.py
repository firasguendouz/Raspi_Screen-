import os
import sys
import time
import subprocess
from server.wifi_config import WiFiConfig
from server.qr_code import generate_wifi_qr
from scripts.connect_wifi import connect_wifi
from scripts.send_activation import ActivationClient

class SetupManager:
    def __init__(self):
        self.wifi_config = WiFiConfig()
        self.activation_client = ActivationClient()

    def start_ap_mode(self):
        """Initialize Access Point mode"""
        try:
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            print("Access Point mode started successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start Access Point mode: {e}")
            return False

    def stop_ap_mode(self):
        """Stop Access Point mode"""
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            print("Access Point mode stopped successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop Access Point mode: {e}")
            return False

    def check_internet_connection(self):
        """Check if device has internet connection"""
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def setup_wifi(self, ssid, password):
        """Configure WiFi connection"""
        return connect_wifi(ssid, password)

    def activate_device(self):
        """Send activation request to central server"""
        success, result = self.activation_client.send_activation_request()
        return success, result

    def start_streaming(self, url):
        """Start streaming mode"""
        try:
            subprocess.Popen(['python3', 'scripts/stream_url.py', url])
            return True
        except Exception as e:
            print(f"Failed to start streaming: {e}")
            return False

def main():
    setup = SetupManager()
    
    # Check if already connected to internet
    if not setup.check_internet_connection():
        print("No internet connection detected. Starting Access Point mode...")
        
        # Start AP mode
        if not setup.start_ap_mode():
            sys.exit(1)
        
        # Generate QR code for AP connection
        generate_wifi_qr("RaspberryAP", "raspberry", "static/qrcode.png")
        
        # Start the configuration web server
        print("Starting configuration web server...")
        subprocess.Popen(['python3', 'server/app.py'])
        
        # Wait for WiFi configuration
        while not setup.check_internet_connection():
            print("Waiting for WiFi configuration...")
            time.sleep(10)
        
        # Stop AP mode once connected
        setup.stop_ap_mode()
    
    print("Internet connection established")
    
    # Attempt device activation
    print("Activating device...")
    success, result = setup.activate_device()
    
    if success:
        print("Device activated successfully")
        
        # Start streaming if URL provided in activation response
        if isinstance(result, dict) and 'stream_url' in result:
            setup.start_streaming(result['stream_url'])
        else:
            print("No streaming URL provided")
    else:
        print(f"Activation failed: {result}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)