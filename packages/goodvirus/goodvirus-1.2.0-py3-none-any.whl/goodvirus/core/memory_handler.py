import os
import json
import hashlib
import datetime
import random
import string

# === PATH SETUP ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MEMORY_FILE = os.path.join(LOGS_DIR, ".gv_memory.json")

# === UTILITY FUNCTIONS ===
def _generate_id():
    """Generate a short unique ID for each flagged file."""
    return "GV-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def _get_timestamp():
    """Return current timestamp as a formatted string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _calculate_hash(file_path):
    """Return SHA256 hash of a file (or None if unreadable)."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

# === MEMORY MANAGEMENT ===
def load_memory():
    """Load memory from JSON, or create if missing."""
    os.makedirs(LOGS_DIR, exist_ok=True)

    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[GooDViruS™] [MEMORY ERROR] Failed to read memory file: {e}")
            return []
    else:
        save_memory([])  # Create empty memory file
        return []

def save_memory(memory):
    """Write memory list to file."""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"[GooDViruS™] [MEMORY ERROR] Could not save memory: {e}")

def remember_file(file_path):
    """
    Track a file based on hash. 
    If it's new, add to memory.
    If renamed, update last_known_name.
    """
    memory = load_memory()
    file_hash = _calculate_hash(file_path)

    if not file_hash:
        return None  # File unreadable or missing

    for entry in memory:
        if entry["hash"] == file_hash:
            if entry["last_known_name"] != file_path:
                entry["last_known_name"] = file_path
                save_memory(memory)
                return {"renamed": True, "entry": entry}
            return {"renamed": False, "entry": entry}

    # New file detected
    new_entry = {
        "hash": file_hash,
        "original_name": file_path,
        "last_known_name": file_path,
        "first_seen": _get_timestamp(),
        "id": _generate_id()
    }
    memory.append(new_entry)
    save_memory(memory)
    return {"new": True, "entry": new_entry}
