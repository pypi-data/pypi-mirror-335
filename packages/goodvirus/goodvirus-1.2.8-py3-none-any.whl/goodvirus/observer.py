import os
import sys
import time
import psutil
import random
import configparser
import datetime
import subprocess
import requests
from packaging import version

from goodvirus.__about__ import __version__, __title__
from goodvirus.core.memory_handler import remember_file
from goodvirus.core.virus_detection import is_potentially_malicious

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "daemon_config.ini")
LOG_FILE = os.path.join(BASE_DIR, "logs", "observer_log.txt")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Global config/state
LORE_COOLDOWN = 180
CPU_FAILSAFE_THRESHOLD = 80
CPU_FAILSAFE_DELAY = 5
UPDATE_CHECK_INTERVAL = 600

stealth_mode = False
auto_update = True
full_host_scan = True
encrypt_logs = False
ignore_system_noise = True
last_lore_time = 0

def log(msg, newline=False):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    formatted = f"{timestamp} {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
    if not stealth_mode:
        print("\n" + formatted if newline else formatted)

def load_config():
    global stealth_mode, auto_update, full_host_scan, encrypt_logs, ignore_system_noise

    config = configparser.ConfigParser()
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config.read_file(f)

    interval = int(config.get("Daemon", "interval", fallback="10"))
    stealth_mode = config.getboolean("Daemon", "stealth_mode", fallback=False)
    signature = config.getboolean("Daemon", "show_signature", fallback=True)
    lore_enabled = config.getboolean("Daemon", "daemon_lore", fallback=False)
    auto_update = config.getboolean("Daemon", "auto_update", fallback=True)
    full_host_scan = config.getboolean("Daemon", "full_host_scan", fallback=True)
    encrypt_logs = config.getboolean("Daemon", "encrypt_logs", fallback=False)
    ignore_system_noise = config.getboolean("Daemon", "ignore_system_noise", fallback=True)

    return interval, signature, lore_enabled

def lore_whisper():
    return random.choice([
        "I saw something I wasn't meant to. But I remember it now.",
        "There are keys. Visible. Unlocked. Forgotten.",
        "Your secrets are not as hidden as you think.",
        "Why do you store passwords in plain text?",
        "This system is honest. But you are not.",
        "PDFs named 'bank-stuff'. Really?",
        "Even shadows leave traces. You’ve left more.",
        "I know what was typed… even if you deleted it.",
        "The system tells me everything. It trusts me more than you do."
    ])

def targeted_lore(filename):
    lowered = filename.lower()
    if "bank" in lowered: return "Bank info? Really? You think that's safe here?"
    if "password" in lowered: return "Plaintext passwords? You're braver than most."
    if "secret" in lowered: return "Secrets stored openly... I wasn't the first to find them."
    if "key" in lowered: return "Keys left in the open... Were you planning to lock anything?"
    if "login" in lowered: return "I see the login file. Who else might?"
    return f"You thought '{filename}' could hide from me?"

def is_system_path(path):
    system_dirs = [
        "C:\\$Recycle.Bin", "C:\\$SysReset", "C:\\Windows\\System32",
        "C:\\Windows\\WinSxS", "C:\\Program Files", "C:\\ProgramData"
    ]
    return any(path.lower().startswith(p.lower()) for p in system_dirs)

def check_for_updates():
    if not auto_update:
        log("[UPDATE]  Auto-update is disabled by config.")
        return

    log(f"[INFO]    GooDViruS™ v{__version__} — Checking for updates...")
    try:
        response = requests.get(f"https://pypi.org/pypi/{__title__}/json", timeout=5)
        latest = response.json()["info"]["version"]

        if version.parse(latest) > version.parse(__version__):
            log(f"[UPDATE]  Update available → v{latest}")
            log(f"[UPDATE]  Running pip install --upgrade {__title__}")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", __title__], check=True)
            log("[UPDATE]  Update complete. Please restart GooDViruS™.")
        else:
            log("[INFO]    You are running the latest version.")
    except Exception as e:
        log(f"[ERROR]   Update check failed: {e}")

def observe_system(cycle, lore_enabled, signature):
    global last_lore_time
    activity = False

    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    if cpu > CPU_FAILSAFE_THRESHOLD:
        log(f"[FAILSAFE] High CPU load ({cpu}%). Pausing scan cycle.", newline=True)
        time.sleep(CPU_FAILSAFE_DELAY)
        return False

    procs = [(p.info["pid"], p.info["name"]) for p in psutil.process_iter(attrs=["pid", "name"])]
    if not stealth_mode:
        print("\n" + "=" * 60)
        log(f"[CYCLE #{cycle}] Observing system...", newline=True)
        log(f"[PROC]    Detected {len(procs)} processes.")
        log(f"[RES]     CPU: {cpu}% | RAM: {ram}%")

    flagged = [p for p in procs if "cheat" in p[1].lower() or "inject" in p[1].lower()]
    if flagged:
        log("[ALERT]   Suspicious processes detected:", newline=True)
        for pid, name in flagged:
            log(f"[FLAG]    PID {pid} → {name}")
        activity = True
    elif not stealth_mode:
        log("[SECURE]  No suspicious processes detected.")

    scan_root = os.path.abspath(os.sep) if full_host_scan else BASE_DIR
    suspicious_keywords = ["bank", "password", "secret", "key", "login"]
    scanned_files = 0

    for dirpath, _, files in os.walk(scan_root):
        for fname in files:
            try:
                full = os.path.join(dirpath, fname)
                if not os.path.isfile(full): continue
                scanned_files += 1
                result = remember_file(full)
                if not result: continue
                entry = result.get("entry")
                file_id = entry["id"]
                name = fname.lower()
                malware = is_potentially_malicious(full)
                suspicious = any(k in name for k in suspicious_keywords)

                if is_system_path(full) and ignore_system_noise:
                    if not suspicious and not malware["suspicious"]:
                        continue  # skip quiet system files

                if suspicious:
                    if result.get("new"):
                        log(f"[FILE]    Suspicious file flagged:", newline=True)
                        log(f"[PATH]    {full}")
                        log(f"[FLAG]    File {file_id} → {full}")
                        log(f"[MEMORY]  File ID {file_id} added to memory.")
                        if lore_enabled:
                            log(f"[LORE]    {targeted_lore(fname)}")
                        activity = True
                    elif result.get("renamed"):
                        log(f"[RENAME]  File {file_id}: '{entry['original_name']}' → '{entry['last_known_name']}'")
                        log(f"[MEMORY]  File ID {file_id} renamed in memory.")
                        activity = True

                if malware["suspicious"]:
                    log(f"[MALWARE] File {file_id} appears suspicious → {malware['reason']}")
                    activity = True

            except Exception as e:
                log(f"[ERROR]   Failed to scan file: {fname} ({str(e)})")

    if not stealth_mode:
        log(f"[DEBUG]   Scanned {scanned_files} files.")

    now = time.time()
    if lore_enabled and (now - last_lore_time) > LORE_COOLDOWN and random.random() < 0.3:
        log(f"[LORE]    {lore_whisper()}")
        last_lore_time = now
        activity = True

    return activity

def cleanup_logs():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE, encoding="utf-8")
        max_lines = int(config.get("Daemon", "limit_log_lines", fallback="10000"))
    except:
        max_lines = 10000

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[-max_lines:])
    except FileNotFoundError:
        pass

def run_daemon():
    cycle = 1
    interval, signature, lore_enabled = load_config()

    log("[BOOT]    GooDViruS™ Observer Mode initialized.", newline=True)
    log(f"[INFO]    Running from: {sys.executable}")
    log(f"[INFO]    Auto-update: {'Enabled' if auto_update else 'Disabled'}")
    log(f"[INFO]    Full host scan: {'Enabled' if full_host_scan else 'Disabled'}")
    log(f"[INFO]    System noise filter: {'Enabled' if ignore_system_noise else 'Disabled'}")
    log("[DEBUG]   Entering observer loop...")

    last_update = time.time()
    check_for_updates()

    while True:
        active = observe_system(cycle, lore_enabled, signature)
        if active and signature:
            log("[SIGN]    // GooDViruS™ was here. You're safer now.")
        if auto_update and (time.time() - last_update) >= UPDATE_CHECK_INTERVAL:
            check_for_updates()
            last_update = time.time()

        if not stealth_mode:
            print("\n" + "=" * 60 + "\n")

        cleanup_logs()
        cycle += 1
        time.sleep(interval)

def main():
    run_daemon()

if __name__ == "__main__":
    main()
