import subprocess
import re
from typing import Dict, Any

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def format_section(title: str) -> str:
    return f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}"

def format_value(label: str, value: str) -> str:
    return f"{Colors.BLUE}{label}:{Colors.ENDC} {Colors.GREEN}{value}{Colors.ENDC}"

def get_cpu_usage() -> str:
    try:
        cmd = "top -bn1 | grep '%Cpu' | awk '{print $2}'"
        return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip() + "%"
    except:
        return "Unknown"

def get_display_info() -> Dict[str, Any]:
    try:
        xrandr_output = subprocess.check_output(['xrandr'], universal_newlines=True)
        connected_display = re.search(r'(\w+) connected (\d+x\d+)', xrandr_output)
        if connected_display:
            return {
                "connection_status": "Connected",
                "resolution": connected_display.group(2)
            }
        return {
            "connection_status": "Disconnected",
            "resolution": "None"
        }
    except Exception as e:
        return {
            "connection_status": f"Error: {str(e)}",
            "resolution": "Unknown"
        }

def get_power_info() -> Dict[str, str]:
    try:
        voltage = subprocess.check_output(['vcgencmd', 'measure_volts', 'core'], universal_newlines=True).strip()
        throttled = subprocess.check_output(['vcgencmd', 'get_throttled'], universal_newlines=True).strip()
        return {
            "voltage": voltage,
            "throttling_state": throttled
        }
    except Exception as e:
        return {
            "voltage": f"Error: {str(e)}",
            "throttling_state": "Unknown"
        }

def is_screen_active() -> bool:
    try:
        output = subprocess.check_output(['xset', 'q'], universal_newlines=True)
        return "Monitor is On" in output
    except:
        return False

def get_wifi_info() -> Dict[str, str]:
    try:
        iwconfig_output = subprocess.check_output(['iwconfig'], universal_newlines=True)
        essid = re.search(r'ESSID:"([^"]+)"', iwconfig_output)
        signal_level = re.search(r'Signal level=(-?\d+ dBm)', iwconfig_output)
        return {
            "essid": essid.group(1) if essid else "Unknown",
            "signal_level": signal_level.group(1) if signal_level else "Unknown"
        }
    except Exception as e:
        return {
            "essid": f"Error: {str(e)}",
            "signal_level": "Unknown"
        }

def get_system_info() -> Dict[str, str]:
    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp'], universal_newlines=True).strip()
        mem = subprocess.check_output(['free', '-h'], shell=True, universal_newlines=True).split('\n')[1].split()
        cpu_usage = get_cpu_usage()
        disk = subprocess.check_output(['df', '-h', '/'], universal_newlines=True).split('\n')[1].split()
        
        return {
            "temperature": temp.replace('temp=', ''),
            "memory_total": mem[1],
            "memory_used": mem[2],
            "memory_free": mem[3],
            "cpu_usage": cpu_usage,
            "disk_total": disk[1],
            "disk_used": disk[2],
            "disk_free": disk[3],
            "disk_usage": disk[4]
        }
    except Exception as e:
        return {
            "temperature": f"Error: {str(e)}",
            "memory_total": "Unknown",
            "memory_used": "Unknown",
            "memory_free": "Unknown",
            "cpu_usage": "Unknown",
            "disk_total": "Unknown",
            "disk_used": "Unknown",
            "disk_free": "Unknown",
            "disk_usage": "Unknown"
        }

def get_network_info() -> Dict[str, str]:
    try:
        ip_address = subprocess.check_output(['hostname', '-I'], universal_newlines=True).strip()
        ifconfig_output = subprocess.check_output(['ifconfig'], universal_newlines=True)
        return {
            "ip_address": ip_address,
            "network_interfaces": ifconfig_output
        }
    except Exception as e:
        return {
            "ip_address": f"Error: {str(e)}",
            "network_interfaces": "Unknown"
        }

def format_network_interface(interface: str, data: str) -> str:
    lines = data.split('\n')
    formatted = f"{Colors.YELLOW}{interface}:{Colors.ENDC}\n"
    for line in lines:
        if line.strip():
            formatted += f"  {line.strip()}\n"
    return formatted

def main():
    print(f"{Colors.BOLD}{Colors.HEADER}🖥️  Raspberry Pi System Monitor 🖥️{Colors.ENDC}")
    
    display_info = get_display_info()
    print(format_section("Display Information"))
    print(format_value("Status", display_info['connection_status']))
    print(format_value("Resolution", display_info['resolution']))
    
    power_info = get_power_info()
    print(format_section("Power Information"))
    print(format_value("Core Voltage", power_info['voltage']))
    print(format_value("Throttling", power_info['throttling_state']))
    
    wifi_info = get_wifi_info()
    print(format_section("WiFi Information"))
    print(format_value("Network", wifi_info['essid']))
    print(format_value("Signal Strength", wifi_info['signal_level']))
    
    system_info = get_system_info()
    print(format_section("System Information"))
    print(format_value("CPU Temperature", system_info['temperature']))
    print(format_value("CPU Usage", system_info['cpu_usage']))
    print(format_value("Memory Total", system_info['memory_total']))
    print(format_value("Memory Used", system_info['memory_used']))
    print(format_value("Memory Free", system_info['memory_free']))
    print(format_value("Disk Total", system_info['disk_total']))
    print(format_value("Disk Used", system_info['disk_used']))
    print(format_value("Disk Free", system_info['disk_free']))
    print(format_value("Disk Usage", system_info['disk_usage']))

    network_info = get_network_info()
    print(format_section("Network Information"))
    print(format_value("IP Address", network_info['ip_address'].split()[0]))
    for interface in ['wlan0', 'eth0', 'lo']:
        if interface in network_info['network_interfaces']:
            iface_data = re.findall(f"{interface}:.*?(?=\n\n|\Z)", 
                                  network_info['network_interfaces'], 
                                  re.DOTALL)[0]
            print(format_network_interface(interface, iface_data))

if __name__ == "__main__":
    main()