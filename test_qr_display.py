import os
import time
import webview
from ui_manager.ui_manager import UIManager
from server.qr_code import generate_wifi_qr
from pathlib import Path

def test_qr_display():
    """Test function to verify QR code display in UI"""
    ui_manager = UIManager()
    
    def webview_ready():
        # Generate test QR
        qr_path = os.path.abspath("test_qr.png")
        generated_path = generate_wifi_qr(
            ssid="TestWiFi",
            password="TestPass123", 
            output_file=qr_path
        )
        
        # Verify file
        if os.path.exists(generated_path):
            print(f"QR Path: {generated_path}")
            print(f"File size: {os.path.getsize(generated_path)} bytes")
            
            # Add delay for UI initialization
            time.sleep(1)
            
            # Display QR
            ui_manager.display_qr_code(
                generated_path,
                "Test QR Code - Please verify display"
            )
        else:
            print("QR file not found!")

    # Create window with debug enabled
    ui_manager.create_ui(webview_ready)

if __name__ == "__main__":
    test_qr_display()