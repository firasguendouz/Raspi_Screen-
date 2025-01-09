# Raspberry Pi Wi-Fi Configuration and Screen Activation System

## Project Overview
This project enables Raspberry Pi devices to serve as screen management systems for hosts. The system performs the following tasks:

1. **Access Point (AP) Creation**: The Raspberry Pi creates a Wi-Fi hotspot if no network is configured.
2. **Configuration Web Page**: A local Flask-based web server allows hosts to input Wi-Fi credentials.
3. **Wi-Fi Connection**: The Raspberry Pi connects to the provided Wi-Fi and verifies the connection.
4. **Screen Activation**: Upon successful connection, the Raspberry Pi communicates with a central server to activate the screen.
5. **Streaming Mode**: After activation, the Raspberry Pi streams advertisements or other content from the server in full-screen mode.

## Project Structure
```
raspi-setup/
├── ap/
│   ├── setup_ap.sh               # Script to initialize Access Point mode
│   ├── stop_ap.sh                # Script to stop Access Point mode
│   └── check_connection.sh       # Script to monitor connectivity and restart AP if necessary
├── server/
│   ├── app.py                    # Flask web server for Wi-Fi configuration
│   ├── qr_code.py                # Generates QR code for AP credentials
│   ├── wifi_config.py            # Handles Wi-Fi setup logic
│   └── __init__.py               # Marks the server folder as a Python module
├── scripts/
│   ├── restart_services.sh       # Restarts network-related services
│   ├── connect_wifi.py           # Connects to the provided Wi-Fi
│   ├── send_activation.py        # Communicates with the central server for activation
│   ├── display_qr_code.py        # Displays a QR code on the screen
│   └── stream_url.py             # Launches the browser for streaming content
├── config/
│   ├── hostapd.conf              # Configuration for hostapd (Access Point)
│   ├── dnsmasq.conf              # Configuration for dnsmasq (DHCP and DNS)
│   └── wpa_supplicant.conf       # Configuration for Wi-Fi credentials
├── static/
│   ├── qrcode.png                # Placeholder for generated QR code
│   ├── default.html              # Default HTML file for offline mode
│   └── logo.png                  # Placeholder for project logo
├── templates/
│   ├── index.html                # Web page for entering Wi-Fi credentials
│   └── success.html              # Confirmation page after successful setup
├── logs/
│   ├── setup.log                 # Log file for setup operations
│   ├── ap.log                    # Log file for Access Point operations
│   └── connection.log            # Log file for connection attempts
├── main.py                       # Main script to orchestrate the workflow
└── README.md                     # Documentation for the project
```

## How to Run the Project

### Prerequisites
1. **Hardware**: Raspberry Pi with Wi-Fi capability.
2. **Software**: Raspbian OS (or similar) installed and updated.
3. **Python**: Ensure Python 3.7+ is installed.
4. **Dependencies**:
   - Flask
   - qrcode
   - requests

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd raspi-setup
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Grant Execution Permissions**:
   ```bash
   chmod +x ap/*.sh
   chmod +x scripts/*.sh
   ```

4. **Run the Main Script**:
   ```bash
   sudo python3 main.py
   ```

5. **Follow On-Screen Instructions**:
   - Connect to the Access Point.
   - Navigate to the local configuration page.
   - Enter Wi-Fi credentials.

6. **Activate the Screen**:
   - After successful Wi-Fi setup, register the screen in the central web application using the displayed unique screen ID.

7. **Streaming Mode**:
   - The Raspberry Pi will switch to streaming mode and begin displaying assigned content.

## To-Do List
This to-do list breaks the project into manageable steps. Cross off tasks as you complete them:

### AP Initialization and Setup
- [ ] Configure `hostapd` for Access Point mode.
- [ ] Configure `dnsmasq` for DHCP and DNS redirection.
- [ ] Create `setup_ap.sh` to initialize AP mode.
- [ ] Create `stop_ap.sh` to stop AP mode.
- [ ] Create `check_connection.sh` to monitor connectivity and restart AP if needed.
- [ ] Implement `qr_code.py` to generate and display QR codes.

### Local Web Server for Wi-Fi Configuration
- [ ] Create Flask server in `app.py`.
- [ ] Implement Wi-Fi credential handling in `wifi_config.py`.
- [ ] Design HTML templates for `index.html` and `success.html`.
- [ ] Test local redirection and form submission.

### Wi-Fi Connection and Validation
- [ ] Write `connect_wifi.py` to apply credentials and test connections.
- [ ] Develop logic to revert to AP mode on failure.
- [ ] Log connection attempts in `connection.log`.

### Communication with Central Server
- [ ] Implement `send_activation.py` to send activation requests.
- [ ] Define server response handling for screen activation and streaming URL.
- [ ] Test server communication for reliability.

### Streaming Mode
- [ ] Implement `stream_url.py` to launch the browser in kiosk mode.
- [ ] Test streaming content with a fallback offline mode.
- [ ] Monitor network status and log in `ap.log`.

### Documentation and Final Testing
- [ ] Update `README.md` with final instructions and troubleshooting steps.
- [ ] Test the entire workflow from AP initialization to streaming mode.
- [ ] Provide detailed error handling for edge cases.

---

This document ensures all contributors understand the project structure, functionality, and setup process. Work through the to-do list step by step, ensuring each feature is tested and functional before proceeding to the next.
