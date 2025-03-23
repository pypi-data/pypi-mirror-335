import tkinter as tk
from tkinter import messagebox
import json
import os
import requests
import subprocess
import sys
from packaging import version
from goodvirus.__about__ import __version__, __title__

CHANGELOG_FILE = os.path.join(os.path.dirname(__file__), "changelog.json")

def show_update_popup(new_version, changes):
    root = tk.Tk()
    root.title("GooDViruS™ Update")
    root.configure(bg="black")
    root.geometry("520x300")
    root.resizable(False, False)

    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    title = tk.Label(frame, text=f"GooDViruS™ Update Available: v{new_version}", fg="lime", bg="black", font=("Consolas", 14, "bold"))
    title.pack(pady=(0, 10))

    change_text = "\n".join(f"• {line}" for line in changes)
    changelog = tk.Label(frame, text=change_text, fg="white", bg="black", font=("Consolas", 10), justify="left")
    changelog.pack(pady=(0, 20))

    def update_now():
        root.destroy()
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", __title__])
        messagebox.showinfo("Update Complete", "GooDViruS™ has been updated.\nPlease restart the daemon.")

    button_frame = tk.Frame(frame, bg="black")
    button_frame.pack()

    tk.Button(button_frame, text="Update Now", command=update_now, bg="lime", fg="black", font=("Consolas", 10, "bold")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancel", command=root.destroy, bg="gray", fg="white", font=("Consolas", 10)).pack(side="left", padx=10)

    root.mainloop()

def check_for_updates():
    print(f"\n🧬 GooDViruS™ v{__version__}")
    print("📦 Checking for updates on PyPI...")

    try:
        response = requests.get(f"https://pypi.org/pypi/{__title__}/json", timeout=5)
        latest = response.json()["info"]["version"]

        if version.parse(latest) > version.parse(__version__):
            changes = []
            if os.path.exists(CHANGELOG_FILE):
                with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
                    all_changes = json.load(f)
                    changes = all_changes.get(latest, [])

            show_update_popup(latest, changes)
        else:
            print("✅ You are running the latest version.\n")

    except Exception as e:
        print(f"⚠️  Could not check for updates: {e}\n")
