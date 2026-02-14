#!/usr/bin/env python3
"""
Script 01: Download Open Food Facts Data

This script downloads the complete Open Food Facts database (compressed JSONL format).
We download the full global database, then filter for German products in the next script.

Learning Points:
- How to download large files with progress tracking
- Working with compressed files (.gz format)
- Basic error handling with try/except

Author: Stephan & Claude
Date: 2025-02-14
"""

import requests  # Library for making HTTP requests
from tqdm import tqdm  # Library for progress bars (makes downloads look nice!)
import os  # For file path operations

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# The URL where Open Food Facts hosts their complete database
# This is a HUGE file (~7-8 GB compressed)
DOWNLOAD_URL = "https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz"

# Where we'll save the downloaded file
# We use os.path.join() to build paths that work on any operating system
OUTPUT_DIR = "/home/claude/sloth/data/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "openfoodfacts-products.jsonl.gz")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def download_file_with_progress(url, destination):
    """
    Downloads a file from a URL and shows a progress bar.
    
    Args:
        url (str): The web address to download from
        destination (str): Where to save the file on disk
        
    Returns:
        bool: True if successful, False if failed
        
    How it works:
    1. Send a GET request with stream=True (downloads in chunks, not all at once)
    2. Get the total file size from the HTTP headers
    3. Open a file to write to
    4. Download chunk by chunk, updating the progress bar
    """
    try:
        print(f"🌐 Starting download from: {url}")
        print(f"📁 Saving to: {destination}\n")
        
        # Send HTTP GET request, but don't download everything yet (stream=True)
        # This lets us download in small pieces
        response = requests.get(url, stream=True)
        
        # Check if the request was successful (status code 200 = OK)
        response.raise_for_status()
        
        # Get the total file size from the HTTP headers
        # int() converts the string to a number
        total_size = int(response.headers.get('content-length', 0))
        
        # Create a progress bar using tqdm
        # unit='B' means bytes, unit_scale=True makes it show MB/GB automatically
        # desc= is the description shown on the left
        progress_bar = tqdm(
            total=total_size, 
            unit='B',           # B = Bytes
            unit_scale=True,    # Automatically convert to KB, MB, GB
            desc="Downloading"
        )
        
        # Open the destination file in binary write mode ('wb')
        # 'with' statement ensures the file closes properly even if there's an error
        with open(destination, 'wb') as file:
            
            # iter_content() downloads in chunks (pieces) rather than all at once
            # chunk_size=8192 means 8 KB at a time (this is efficient)
            for chunk in response.iter_content(chunk_size=8192):
                
                # Write this chunk to the file
                file.write(chunk)
                
                # Update the progress bar by the size of this chunk
                progress_bar.update(len(chunk))
        
        # Close the progress bar
        progress_bar.close()
        
        print("\n✅ Download complete!")
        return True
        
    except requests.exceptions.RequestException as e:
        # If anything goes wrong with the download, catch the error here
        print(f"\n❌ Error downloading file: {e}")
        return False
    except IOError as e:
        # If anything goes wrong with writing to disk, catch it here
        print(f"\n❌ Error writing file: {e}")
        return False

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    """
    This code only runs if we execute this script directly.
    If we import this file as a module, this part won't run.
    """
    
    print("="*70)
    print("OPEN FOOD FACTS DOWNLOADER")
    print("="*70)
    print()
    
    # Check if the file already exists
    if os.path.exists(OUTPUT_FILE):
        print(f"⚠️  File already exists: {OUTPUT_FILE}")
        
        # Ask the user if they want to re-download
        response = input("Do you want to re-download? (y/n): ").lower()
        
        if response != 'y':
            print("Skipping download. Using existing file.")
            exit(0)  # Exit the script with success code 0
    
    # Make sure the output directory exists
    # exist_ok=True means "don't error if it already exists"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Call our download function
    success = download_file_with_progress(DOWNLOAD_URL, OUTPUT_FILE)
    
    if success:
        # Get the file size in MB for confirmation
        file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)  # Bytes to MB
        print(f"📊 File size: {file_size:.2f} MB")
        print(f"📍 Location: {OUTPUT_FILE}")
        print("\n🎉 Ready for the next step: filtering German products!")
    else:
        print("\n😞 Download failed. Please check your internet connection and try again.")
        exit(1)  # Exit with error code 1

"""
NEXT STEPS:
After running this script, you'll have a huge compressed file with ALL products worldwide.
In script 02, we'll filter this down to just German products!
"""
