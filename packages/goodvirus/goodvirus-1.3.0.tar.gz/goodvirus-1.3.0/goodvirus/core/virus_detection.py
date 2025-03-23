import os
import math

# Suspicious file types often used in malware
SUSPICIOUS_EXTENSIONS = [
    ".exe", ".dll", ".scr", ".bat", ".cmd", ".pyc", ".jar", ".bin"
]

# Entropy threshold: high values can indicate compression or encryption
ENTROPY_THRESHOLD = 7.5  # Max is ~8.0

def _get_file_extension(file_path):
    """Return the lowercase file extension."""
    return os.path.splitext(file_path)[1].lower()

def calculate_entropy(file_path):
    """
    Calculate Shannon entropy of file content.
    High entropy may suggest encryption, compression, or obfuscation.
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            if not data:
                return 0.0
            byte_freq = [0] * 256
            for byte in data:
                byte_freq[byte] += 1
            entropy = -sum((count / len(data)) * math.log2(count / len(data))
                           for count in byte_freq if count)
            return entropy
    except Exception:
        return 0.0  # Fail-safe: unreadable or locked files return 0

def is_potentially_malicious(file_path):
    """
    Heuristic-based evaluation to detect suspicious files.
    Uses entropy + file type logic.
    Returns:
        - {"suspicious": True, "reason": "..."} if flagged
        - {"suspicious": False} otherwise
    """
    extension = _get_file_extension(file_path)
    entropy = calculate_entropy(file_path)

    if extension in SUSPICIOUS_EXTENSIONS and entropy >= ENTROPY_THRESHOLD:
        return {
            "suspicious": True,
            "reason": f"High entropy ({entropy:.2f}) with suspicious extension {extension}"
        }

    return {"suspicious": False}
