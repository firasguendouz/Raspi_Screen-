import qrcode

def generate_wifi_qr(ssid, password, output_file="wifi_qr.png"):
    """
    Generate a QR code for Wi-Fi credentials.

    Args:
        ssid (str): Wi-Fi network name.
        password (str): Wi-Fi password.
        output_file (str): Filename for the generated QR code image.
    """
    try:
        # Format Wi-Fi credentials in QR code format
        wifi_string = f"WIFI:T:WPA;S:{ssid};P:{password};;"

        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(wifi_string)
        qr.make(fit=True)

        # Save the QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_file)

        print(f"QR code generated successfully: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    ssid = "RaspberryAP"
    password = "raspberry"
    generate_wifi_qr(ssid, password)
