"""
Download the Open Food Facts JSONL dump.

Downloads the complete database (~7-8GB compressed) from the OFF static server.
Supports resume via HTTP Range headers if the download is interrupted.

Usage:
    cd backend
    python scripts/pipeline/off_download.py
"""

import os
import sys
import requests
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DOWNLOAD_URL = "https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz"
USER_AGENT = "SlothDietApp/1.0 (sloth-diet-app; German grocery pipeline)"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "openfoodfacts-products.jsonl.gz"


def download_off_dump():
    """Download the OFF JSONL dump with resume support."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": USER_AGENT}
    resume_byte = 0

    if OUTPUT_FILE.exists():
        resume_byte = OUTPUT_FILE.stat().st_size
        print(f"Existing file found: {resume_byte / 1e9:.2f} GB")
        headers["Range"] = f"bytes={resume_byte}-"

    print(f"Downloading from: {DOWNLOAD_URL}")
    print(f"Saving to: {OUTPUT_FILE}")

    try:
        resp = requests.get(DOWNLOAD_URL, headers=headers, stream=True, timeout=30)
    except requests.RequestException as e:
        print(f"ERROR: Failed to connect: {e}")
        sys.exit(1)

    # Check if server supports resume
    if resume_byte > 0 and resp.status_code == 416:
        print("File already fully downloaded.")
        return
    elif resume_byte > 0 and resp.status_code == 206:
        print(f"Resuming download from byte {resume_byte}...")
        mode = "ab"
    elif resp.status_code == 200:
        if resume_byte > 0:
            print("Server does not support resume, starting fresh...")
        mode = "wb"
        resume_byte = 0
    else:
        print(f"ERROR: HTTP {resp.status_code}")
        sys.exit(1)

    # Get total size
    content_length = resp.headers.get("Content-Length")
    if content_length:
        total_bytes = int(content_length) + resume_byte
    else:
        total_bytes = None

    # Try to use tqdm for progress, fall back to simple counter
    try:
        from tqdm import tqdm
        progress = tqdm(
            total=total_bytes,
            initial=resume_byte,
            unit="B",
            unit_scale=True,
            desc="Downloading OFF dump",
        )
        use_tqdm = True
    except ImportError:
        print("(Install tqdm for a progress bar: pip install tqdm)")
        use_tqdm = False
        downloaded = resume_byte

    CHUNK_SIZE = 8192
    with open(OUTPUT_FILE, mode) as f:
        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                if use_tqdm:
                    progress.update(len(chunk))
                else:
                    downloaded += len(chunk)
                    if downloaded % (50 * 1024 * 1024) < CHUNK_SIZE:  # every ~50MB
                        if total_bytes:
                            pct = downloaded / total_bytes * 100
                            print(f"  {downloaded / 1e9:.2f} / {total_bytes / 1e9:.2f} GB ({pct:.1f}%)")
                        else:
                            print(f"  {downloaded / 1e9:.2f} GB downloaded...")

    if use_tqdm:
        progress.close()

    final_size = OUTPUT_FILE.stat().st_size
    print(f"\nDone! File size: {final_size / 1e9:.2f} GB")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    download_off_dump()
