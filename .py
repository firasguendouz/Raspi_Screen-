import os

def create_project_structure(base_dir="raspi-setup"):
    structure = {
        "ap": ["setup_ap.sh", "stop_ap.sh", "check_connection.sh"],
        "server": ["app.py", "qr_code.py", "wifi_config.py", "__init__.py"],
        "scripts": ["restart_services.sh", "connect_wifi.py", "send_activation.py", "display_qr_code.py", "stream_url.py"],
        "config": ["hostapd.conf", "dnsmasq.conf", "wpa_supplicant.conf"],
        "static": ["qrcode.png", "default.html", "logo.png"],
        "templates": ["index.html", "success.html"],
        "logs": ["setup.log", "ap.log", "connection.log"]
    }
    
    files_at_root = ["main.py", "README.md"]

    # Create base directory
    os.makedirs(base_dir, exist_ok=True)

    # Create subdirectories and files
    for folder, files in structure.items():
        folder_path = os.path.join(base_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'w') as f:
                f.write("")  # Create an empty file

    # Create root-level files
    for file in files_at_root:
        file_path = os.path.join(base_dir, file)
        with open(file_path, 'w') as f:
            f.write("")  # Create an empty file

    print(f"Project structure created at '{base_dir}'")

# Run the function to generate the structure
create_project_structure()
