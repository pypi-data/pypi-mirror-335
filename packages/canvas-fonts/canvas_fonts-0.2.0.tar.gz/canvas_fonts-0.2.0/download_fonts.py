import os
import requests
import time
from pathlib import Path
from canvas_fonts.data import FONTS

# Create fonts directory if it doesn't exist
FONTS_DIR = Path(__file__).parent / "canvas_fonts" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

def format_font_url(font_name):
    """Format the font name for the Google Fonts URL."""
    # Remove spaces and special characters
    formatted_name = font_name.replace(' ', '+')
    return f"https://fonts.google.com/download?family={formatted_name}"

def download_font(font_name, retry_count=3, delay=1):
    """Download a font from Google Fonts with retry mechanism."""
    url = format_font_url(font_name)
    
    for attempt in range(retry_count):
        try:
            print(f"Downloading {font_name} from {url} (attempt {attempt + 1}/{retry_count})")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
            
            if response.status_code == 200:
                # Save the TTF file
                font_filename = f"{font_name.replace(' ', '')}.ttf"
                font_path = FONTS_DIR / font_filename
                
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Successfully downloaded {font_name}")
                return True
            elif response.status_code == 429:  # Too Many Requests
                print(f"Rate limited while downloading {font_name}, waiting before retry...")
                time.sleep(delay * (attempt + 1))  # Exponential backoff
                continue
            else:
                print(f"Failed to download {font_name}: HTTP {response.status_code}")
                if attempt < retry_count - 1:
                    time.sleep(delay)
                    continue
                return False
                
        except Exception as e:
            print(f"Error downloading {font_name}: {str(e)}")
            if attempt < retry_count - 1:
                time.sleep(delay)
                continue
            return False
    
    return False

def main():
    """Download all fonts from Google Fonts with progress tracking."""
    total_fonts = len(FONTS)
    print(f"Starting download of {total_fonts} fonts to {FONTS_DIR}")
    print("This may take a while due to rate limiting and retries...")
    
    success_count = 0
    failed_fonts = []
    
    for i, font in enumerate(FONTS, 1):
        print(f"\nProcessing font {i}/{total_fonts}: {font}")
        if download_font(font):
            success_count += 1
        else:
            failed_fonts.append(font)
        
        # Add a small delay between downloads to avoid rate limiting
        if i < total_fonts:
            time.sleep(0.5)
    
    print(f"\nDownload Summary:")
    print(f"✓ Successfully downloaded: {success_count} fonts")
    print(f"✗ Failed to download: {len(failed_fonts)} fonts")
    
    if failed_fonts:
        print("\nFailed fonts:")
        for font in failed_fonts:
            print(f"- {font}")
        
        # Save failed fonts to a file for later retry
        with open("failed_fonts.txt", "w") as f:
            f.write("\n".join(failed_fonts))
        print("\nFailed fonts list has been saved to 'failed_fonts.txt'")

if __name__ == "__main__":
    main() 