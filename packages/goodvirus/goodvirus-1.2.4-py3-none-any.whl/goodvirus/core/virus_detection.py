import os
import math

# List of suspicious file extensions
SUSPICIOUS_EXTENSIONS = [".exe", ".dll", ".scr", ".bat", ".cmd", ".pyc", ".jar", ".bin"]

# Files with high entropy (compressed/encrypted) may be malware
ENTROPY_THRESHOLD = 7.5  # max is ~8.0

def _get_file_extension(file_path):
    return os.path.splitext(file_path)[1].lower()

def calculate_entropy(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            if not data:
                return 0.0
            byte_freq = [0] * 256
            for byte in data:
                byte_freq[byte] += 1
            entropy = 0
            for count in byte_freq:
                if count:
                    p = count / len(data)
                    entropy -= p * math.log2(p)
            return entropy
    except Exception:
        return 0.0  # unreadable = ignore

def is_potentially_malicious(file_path):
    extension = _get_file_extension(file_path)
    entropy = calculate_entropy(file_path)

    if extension in SUSPICIOUS_EXTENSIONS and entropy >= ENTROPY_THRESHOLD:
        return {
            "suspicious": True,
            "reason": f"High entropy ({entropy:.2f}) with suspicious extension {extension}"
        }

    return {"suspicious": False}
