import os
import urllib.request
from pathlib import Path

# Category Keywords for Unsplash
CATEGORIES = {
    'Electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800',
    'Fashion': 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800',
    'Home Decor': 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800',
    'Handicrafts': 'https://images.unsplash.com/photo-1515516089376-88db1e26e9c0?w=800',
    'Organic Food': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=800'
}

MEDIA_DIR = Path('media/products')
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def download_images():
    # Set a user-agent to avoid being blocked
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    for name, url in CATEGORIES.items():
        filename = name.lower().replace(' ', '_') + '.jpg'
        filepath = MEDIA_DIR / filename
        
        print(f"Downloading {name} image...")
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"Successfully downloaded {filename}")
        except Exception as e:
            print(f"Error downloading {name}: {e}")

if __name__ == '__main__':
    download_images()
