import tkinter as tk
import subprocess
import sys
import json
import os

def load_changelog(version):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        changelog_path = os.path.join(base_path, "..", "changelog.json")
        with open(changelog_path, "r", encoding="utf-8") as f:
            all_logs = json.load(f)
        entries = all_logs.get(version, ["No changelog found."])
        return "\n".join(f"• {entry}" for entry in entries)
    except Exception as e:
        return f"Could not load changelog: {e}"

def show_update_popup(current_version, latest_version, changelog=None):
    changelog = changelog or load_changelog(latest_version)

    window = tk.Tk()
    window.title("GooDViruS™ Update Available")
    window.configure(bg="black")
    window.geometry("460x300")
    window.resizable(False, False)

    tk.Label(window, text="⚠️ GooDViruS™ Update Available", fg="white", bg="black", font=("Consolas", 14, "bold")).pack(pady=(10, 5))
    tk.Label(window, text=f"Current Version: {current_version}", fg="white", bg="black", font=("Consolas", 10)).pack()
    tk.Label(window, text=f"New Version: {latest_version}", fg="#00ff00", bg="black", font=("Consolas", 10)).pack()

    frame = tk.Frame(window, bg="black")
    frame.pack(padx=15, pady=(10, 5), fill="both", expand=True)

    changelog_box = tk.Text(frame, wrap="word", bg="black", fg="white", font=("Consolas", 9))
    changelog_box.insert("1.0", changelog.strip())
    changelog_box.config(state="disabled")
    changelog_box.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame, command=changelog_box.yview)
    scrollbar.pack(side="right", fill="y")
    changelog_box.config(yscrollcommand=scrollbar.set)

    def update_now():
        window.destroy()
        subprocess.Popen([sys.executable, "-m", "pip", "install", "--upgrade", "goodvirus"])

    def cancel():
        window.destroy()

    btn_frame = tk.Frame(window, bg="black")
    btn_frame.pack(pady=(10, 10))

    tk.Button(btn_frame, text="Update Now", command=update_now, bg="#007700", fg="white", font=("Consolas", 10)).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", command=cancel, bg="#770000", fg="white", font=("Consolas", 10)).pack(side="left", padx=10)

    window.mainloop()
