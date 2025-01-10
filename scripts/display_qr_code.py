import os
import qrcode
from PIL import Image

def generate_and_display_qr(ssid, password):
    """
    Generate and display a QR code for Wi-Fi credentials.

    Args:
        ssid (str): Wi-Fi network name.
        password (str): Wi-Fi password.
    """
    try:
        # Format Wi-Fi credentials in the standard Wi-Fi QR code format
        wifi_string = f"WIFI:T:WPA;S:{ssid};P:{password};;"

        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(wifi_string)
        qr.make(fit=True)

        # Generate the QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        output_file = "wifi_qr.png"
        qr_image.save(output_file)

        # Display the QR code using the default image viewer
        print(f"QR code saved as {output_file}")
        Image.open(output_file).show()

    except Exception as e:
        print(f"Error generating or displaying QR code: {e}")

if __name__ == "__main__":
    # Example usage
    ssid = "RaspberryAP"
    password = "raspberry"
    generate_and_display_qr(ssid, password)
