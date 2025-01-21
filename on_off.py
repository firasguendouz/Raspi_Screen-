import os
import sys
import subprocess
import time

def get_active_display():
    try:
        cmd = "xrandr | grep ' connected' | cut -f1 -d' '"
        display = subprocess.check_output(cmd, shell=True).decode().strip()
        if not display:
            raise Exception("No display found")
        return display
    except Exception as e:
        print(f"Error detecting display: {e}")
        sys.exit(1)

def turn_screen_on():
    try:
        display = get_active_display()
        # Force screen on and disable power saving
        os.system(f"xrandr --output {display} --auto")
        os.system("xset dpms force on")
        os.system("xset s off")
        os.system("xset -dpms")
        print(f"Screen {display} turned ON")
    except Exception as e:
        print(f"Error turning screen on: {e}")

def turn_screen_off():
    try:
        display = get_active_display()
        # Force screen off and enable power saving
        os.system("xset +dpms")
        os.system("xset dpms 0 0 0")
        os.system(f"xrandr --output {display} --off")
        print(f"Screen {display} turned OFF")
    except Exception as e:
        print(f"Error turning screen off: {e}")

def set_brightness(level):
    try:
        display = get_active_display()
        brightness = level / 10.0
        result = os.system(f"xrandr --output {display} --brightness {brightness}")
        if result == 0:
            print(f"Brightness set to level {level} ({brightness:.1f}) on {display}")
        else:
            print("Failed to set brightness")
    except Exception as e:
        print(f"Error setting brightness: {e}")

def rotate_screen(orientation):
    try:
        display = get_active_display()
        os.system(f"xrandr --output {display} --rotate {orientation}")
        print(f"Screen rotated to {orientation}")
    except Exception as e:
        print(f"Error rotating screen: {e}")

def get_rotation_choice():
    print("\nRotation Options:")
    print("1. Normal (0°)")
    print("2. Right (90°)")
    print("3. Inverted (180°)")
    print("4. Left (270°)")
    while True:
        choice = input("Enter rotation choice (1-4): ")
        rotations = {
            "1": "normal",
            "2": "right",
            "3": "inverted",
            "4": "left"
        }
        if choice in rotations:
            return rotations[choice]
        print("Invalid choice! Please select 1-4")

def display_menu():
    print("\nScreen Control Menu:")
    print("1. Turn Screen ON")
    print("2. Turn Screen OFF")
    print("3. Set Brightness")
    print("4. Rotate Screen")
    print("5. Exit")

def get_brightness_level():
    while True:
        try:
            level = int(input("Enter brightness level (1-10): "))
            if 1 <= level <= 10:
                return level
            print("Please enter a number between 1 and 10")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            turn_screen_on()
        elif choice == "2":
            turn_screen_off()
        elif choice == "3":
            level = get_brightness_level()
            set_brightness(level)
        elif choice == "4":
            orientation = get_rotation_choice()
            rotate_screen(orientation)
        elif choice == "5":
            print("Exiting program...")
            sys.exit(0)
        else:
            print("Invalid choice! Please select 1-5")
        
        time.sleep(1)

if __name__ == "__main__":
    main()