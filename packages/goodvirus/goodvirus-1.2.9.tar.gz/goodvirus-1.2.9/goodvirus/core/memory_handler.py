import os
import json
import hashlib
import datetime
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
MEMORY_FILE = os.path.join(LOG_DIR, "gv_memory.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config", "daemon_config.ini")

os.makedirs(LOG_DIR, exist_ok=True)

def load_config_limit():
    config = ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    return int(config.get("Daemon", "limit_memory_entries", fallback="1000"))

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(memory):
    max_entries = load_config_limit()
    if len(memory) > max_entries:
        memory = memory[-max_entries:]

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def hash_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def remember_file(path):
    memory = load_memory()
    file_hash = hash_file(path)
    if not file_hash:
        return None

    existing = next((entry for entry in memory if entry["hash"] == file_hash), None)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if existing:
        if existing["last_known_name"] != path:
            existing["last_known_name"] = path
            save_memory(memory)
            return {"renamed": True, "entry": existing}
        return None

    file_id = f"GV-{os.urandom(2).hex().upper()}"
    new_entry = {
        "id": file_id,
        "hash": file_hash,
        "original_name": path,
        "last_known_name": path,
        "first_seen": now
    }
    memory.append(new_entry)
    save_memory(memory)
    return {"new": True, "entry": new_entry}
