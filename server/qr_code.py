import qrcode
import json
import os

def generate_wifi_qr(ssid, password, filename="wifi_qr.png"):
    """
    Generate a QR code for WiFi credentials
    
    Args:
        ssid (str): WiFi network name
        password (str): WiFi password
        filename (str): Output filename for QR code image
    """
    # Format the WiFi credentials in the standard WiFi QR code format
    wifi_string = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data(wifi_string)
    qr.make(fit=True)
    
    # Create image from QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save the QR code image
    qr_image.save(filename)
    
    return filename

def read_credentials():
    """Read WiFi credentials from config file"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('ssid'), config.get('password')
    except FileNotFoundError:
        return None, None

if __name__ == "__main__":
    ssid, password = read_credentials()
    
    if ssid and password:
        qr_file = generate_wifi_qr(ssid, password)
        print(f"QR code generated successfully: {qr_file}")
    else:
        print("Error: Could not read WiFi credentials from config.json")