import os
import requests
from pathlib import Path

# Create fonts directory if it doesn't exist
FONTS_DIR = Path(__file__).parent / "canvas_fonts" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Font download URLs
FONT_URLS = {
    "Roboto": "https://fonts.google.com/download?family=Roboto",
    "OpenSans": "https://fonts.google.com/download?family=Open+Sans",
    "Lato": "https://fonts.google.com/download?family=Lato",
    "Montserrat": "https://fonts.google.com/download?family=Montserrat",
    "SourceCodePro": "https://fonts.google.com/download?family=Source+Code+Pro"
}

def download_font(font_name, url):
    """Download a font from Google Fonts."""
    try:
        # Download the zip file
        print(f"Downloading {font_name} from {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, allow_redirects=True)
        
        if response.status_code == 200:
            # Save the regular TTF file
            font_filename = f"{font_name}.ttf"
            font_path = FONTS_DIR / font_filename
            
            with open(font_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {font_name} to {font_path}")
            return True
        else:
            print(f"Failed to download {font_name}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error downloading {font_name}: {str(e)}")
        return False

def main():
    """Download all fonts from Google Fonts."""
    print(f"Downloading {len(FONT_URLS)} fonts to {FONTS_DIR}")
    
    success_count = 0
    for font_name, url in FONT_URLS.items():
        if download_font(font_name, url):
            success_count += 1
    
    print(f"\nDownloaded {success_count} out of {len(FONT_URLS)} fonts successfully")

if __name__ == "__main__":
    main() 