import requests
import subprocess
import sys
from goodvirus.__about__ import __version__, __title__

def check_for_updates(auto_update=True):
    print(f"\n🧬 GooDViruS™ v{__version__}")
    print("📦 Checking for updates on PyPI...")

    try:
        response = requests.get(f"https://pypi.org/pypi/{__title__}/json", timeout=5)
        data = response.json()
        latest_version = data["info"]["version"]

        if __version__ != latest_version:
            print(f"⬆️  Update available! Upgrading to v{latest_version}...")

            if auto_update:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", __title__], check=True)
                print("✅ Update complete. Please restart GooDViruS™.\n")
            else:
                print("⚠️  Run manually: pip install --upgrade goodvirus\n")
        else:
            print("✅ You are running the latest version.\n")

    except Exception as e:
        print(f"⚠️  Could not check for updates: {e}\n")
