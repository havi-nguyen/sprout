import subprocess

def check_dsi_display():
    try:
        # Run vcgencmd command to check display power
        output = subprocess.check_output(["vcgencmd", "display_power"], universal_newlines=True)
        if "display_power=1" in output:
            print("DSI display is connected and powered on.")
        else:
            print("DSI display is not connected or powered off.")
    except subprocess.CalledProcessError:
        print("Failed to check DSI display status. Ensure vcgencmd is available.")

check_dsi_display()