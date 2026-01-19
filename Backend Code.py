import subprocess
import datetime
import csv
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_wifi_profiles():
    command = ["netsh", "wlan", "show", "profiles"]
    output = subprocess.check_output(command).decode(errors="ignore")
    return [line.split(":")[1].strip() for line in output.split("\n") if "All User Profile" in line]

def get_wifi_password(profile):
    try:
        command = ["netsh", "wlan", "show", "profile", profile, "key=clear"]
        output = subprocess.check_output(command).decode(errors="ignore")
        for line in output.split("\n"):
            if "Key Content" in line:
                return line.split(":")[1].strip()
    except subprocess.CalledProcessError:
        pass
    return "Not Available"

def fetch_wifi_data():
    data = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for profile in get_wifi_profiles():
        password = get_wifi_password(profile)
        data.append((profile, password, timestamp))

    return data

def export_to_csv(data):
    filename = f"wifi_passwords_{datetime.date.today()}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["WiFi Name", "Password", "Fetched On"])
        writer.writerows(data)
    return os.path.abspath(filename)
