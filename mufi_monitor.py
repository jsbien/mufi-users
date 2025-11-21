import hashlib
import requests
from datetime import datetime
from pathlib import Path
import difflib

URL = "https://mufi.info/"
SNAPSHOT_DIR = Path("snapshots")
HASH_FILE = Path("last_hash.txt")
LATEST_FILE = SNAPSHOT_DIR / "latest.html"

def fetch_page():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    return response.text

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def load_last_snapshot() -> str:
    return LATEST_FILE.read_text(encoding="utf-8") if LATEST_FILE.exists() else ""

def save_snapshot(content: str, hash_value: str):
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")

    # Save raw HTML
    with open(SNAPSHOT_DIR / f"{timestamp}.html", "w", encoding="utf-8") as f:
        f.write(content)

    # Save human-readable diff
    old_content = load_last_snapshot().splitlines()
    new_content = content.splitlines()
    diff = difflib.unified_diff(
        old_content, new_content,
        fromfile='previous.html',
        tofile='current.html',
        lineterm=''
    )
    with open(SNAPSHOT_DIR / f"{timestamp}.diff.txt", "w", encoding="utf-8") as f:
        f.write('\n'.join(diff))

    # Update latest version and hash
    LATEST_FILE.write_text(content, encoding="utf-8")
    HASH_FILE.write_text(hash_value)

    return f"{timestamp}.diff.txt"

def main():
    html = fetch_page()
    new_hash = compute_hash(html)
    old_hash = HASH_FILE.read_text().strip() if HASH_FILE.exists() else ""

    if new_hash != old_hash:
        print("🔔 Change detected. Saving snapshot and diff.")
        diff_file = save_snapshot(html, new_hash)
        return diff_file
    else:
        print("✅ No change detected.")
        return ""

if __name__ == "__main__":
    main()
