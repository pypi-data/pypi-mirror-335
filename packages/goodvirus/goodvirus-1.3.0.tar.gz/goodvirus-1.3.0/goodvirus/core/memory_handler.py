import os
import json
import hashlib
import datetime
from configparser import ConfigParser

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
MEMORY_FILE = os.path.join(LOG_DIR, "gv_memory.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config", "daemon_config.ini")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def load_config_limit():
    """Load maximum memory entry limit from config file."""
    config = ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    return int(config.get("Daemon", "limit_memory_entries", fallback="1000"))

def load_memory():
    """Load memory entries from JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(memory):
    """Save memory list to JSON file, respecting configured entry limit."""
    max_entries = load_config_limit()
    if len(memory) > max_entries:
        memory = memory[-max_entries:]  # Keep only the most recent entries
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to write memory file: {e}")

def hash_file(path):
    """Generate SHA-256 hash of the file contents."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def remember_file(path):
    """
    Track and identify files using content hashing.
    Flags new files, and detects renamed ones by hash.
    Returns:
        - {'new': True, 'entry': ...} if the file is newly flagged.
        - {'renamed': True, 'entry': ...} if a known file was renamed.
        - None if already known and unchanged.
    """
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

    # Assign unique ID for the new flagged file
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
