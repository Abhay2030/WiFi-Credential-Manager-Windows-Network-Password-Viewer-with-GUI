import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import csv
import ctypes
import os
from datetime import datetime

# --- BACKEND LOGIC (The missing functions) ---

def is_admin():
    """Checks if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def fetch_wifi_data():
    """Retrieves Wi-Fi names and passwords using Windows Netsh."""
    data = []
    try:
        # Get list of profiles
        meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="backslashreplace").split('\n')
        profiles = [i.split(":")[1][1:-1] for i in meta_data if "All User Profile" in i]

        for profile in profiles:
            try:
                # Get password for each profile
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8', errors="backslashreplace").split('\n')
                passwords = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                
                password = passwords[0] if passwords else ""
                fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data.append((profile, password, fetch_time))
            except subprocess.CalledProcessError:
                continue
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    return data

def export_to_csv(data):
    """Exports the fetched data to a CSV file."""
    filename = "wifi_credentials.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["WiFi Name", "Password", "Fetched On"])
        writer.writerows(data)
    return os.path.abspath(filename)

# --- FRONTEND LOGIC ---

def load_data():
    table.delete(*table.get_children())
    wifi_data = fetch_wifi_data()
    for wifi in wifi_data:
        table.insert("", tk.END, values=wifi)

def export_data():
    data = fetch_wifi_data()
    if not data:
        messagebox.showwarning("No Data", "No Wi-Fi data found to export.")
        return
    path = export_to_csv(data)
    messagebox.showinfo("Export Successful", f"File saved at:\n{path}")

# --- APP INITIALIZATION ---

# Check for admin rights before launching GUI
if not is_admin():
    # Note: netsh often requires admin to see passwords
    messagebox.showerror("Permission Error", "Please run this program as Administrator to view passwords.")
    exit()

root = tk.Tk()
root.title("Wi-Fi Credential Manager")
root.geometry("750x450")

title = tk.Label(root, text="Wi-Fi Network Credential Viewer", font=("Segoe UI", 16, "bold"))
title.pack(pady=10)

columns = ("WiFi Name", "Password", "Fetched On")
table = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=220)

table.pack(expand=True, fill="both", padx=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Load Networks", command=load_data).pack(side="left", padx=10)
ttk.Button(btn_frame, text="Export to CSV", command=export_data).pack(side="left", padx=10)

root.mainloop()