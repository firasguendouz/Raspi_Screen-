import qrcode
import json

def generate_qr_code(data, output_file, qr_type="wifi"):
    """
    Unified QR code generator for both WiFi and URL data.
    
    Args:
        data (dict or str): For WiFi: dict with ssid/password, For URL: string
        output_file (str): Path to save QR code image
        qr_type (str): Either "wifi" or "url"
    
    Returns:
        str: Path to generated QR code file or None if failed
    """
    try:
        if qr_type == "wifi" and isinstance(data, dict):
            qr_string = f"WIFI:T:WPA;S:{data['ssid']};P:{data['password']};;"
        elif qr_type == "url" and isinstance(data, str):
            qr_string = data
        else:
            raise ValueError("Invalid data format for QR type")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)

        # Create and save image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_file)
        print(f"QR code generated successfully: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

# Helper functions for specific QR types
def generate_wifi_qr(ssid, password, output_file="wifi_qr.png"):
    """Generate WiFi connection QR code"""
    data = {"ssid": ssid, "password": password}
    return generate_qr_code(data, output_file, "wifi")

def generate_url_qr(url, output_file="url_qr.png"):
    """Generate URL redirect QR code"""
    return generate_qr_code(url, output_file, "url")