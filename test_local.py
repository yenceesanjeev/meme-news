import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Constants
MEME_DIR = 'docs/meme_images'
JSON_FILE = 'docs/memes.json'

# Create directories
if not os.path.exists(MEME_DIR):
    os.makedirs(MEME_DIR, exist_ok=True)
if not os.path.exists(os.path.dirname(JSON_FILE)):
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)

def load_json():
    """Load existing JSON data"""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    return {'news': []}

def save_json(data):
    """Save data to JSON file"""
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def fetch_news():
    """Fetch first 5 news items"""
    api_key = os.getenv('NEWS_API_KEY')
    url = f'https://newsdata.io/api/1/news?apikey={api_key}&q=technology&country=gb,us&language=en&category=business,education,entertainment,science,technology'
    
    print("\nFetching news...")
    try:
        response = requests.get(url)
        data = response.json()
        news_items = data['results'][:5]  # Get only first 5 items
        print(f"✅ Fetched {len(news_items)} news items!")
        return news_items
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return None

def generate_memes(text):
    """Generate multiple memes for a news item"""
    api_key = os.getenv('MEME_API_KEY')
    url = 'https://dev.supermeme.ai/api/v2/meme/image'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"\nGenerating memes for title: {text[:50]}...")
    try:
        # Get meme URLs from Supermeme
        response = requests.post(url, headers=headers, json={'text': text})
        all_meme_urls = response.json()['memes']
        meme_paths = []
        
        # Download and save each meme
        for i, meme_url in enumerate(all_meme_urls, 1):
            img_response = requests.get(meme_url)
            if img_response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'meme_{timestamp}_{i}.jpg'
                filepath = os.path.join(MEME_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                meme_paths.append(filename)
                print(f"✅ Saved meme {i}/{len(all_meme_urls)}")
        
        print(f"✅ Generated and saved {len(meme_paths)} memes!")
        return meme_paths
    except Exception as e:
        print(f"❌ Error generating memes: {e}")
        return []

def save_memes(news_item, meme_paths):
    """Save meme data to JSON"""
    print("\nSaving to JSON...")
    try:
        data = load_json()
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        news_entry = {
            'title': news_item['title'],
            'date': news_item.get('pubDate', ''),
            'generated_at': current_date,
            'meme_files': meme_paths
        }
        
        # Add to start of list (newest first)
        data['news'].insert(0, news_entry)
        
        # Keep only last 50 news items
        data['news'] = data['news'][:50]
        
        save_json(data)
        print(f"✅ Saved news with {len(meme_paths)} memes to JSON!")
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")

def view_memes():
    """View all memes in JSON"""
    print("\nViewing memes...")
    data = load_json()
    
    for news in data['news']:
        print("-" * 50)
        print(f"Title: {news['title'][:50]}...")
        print(f"Date: {news['date']}")
        print(f"Generated: {news['generated_at']}")
        print("Meme files:")
        for meme_file in news['meme_files']:
            print(f"  - {meme_file}")
    
def main():
    """Main function"""
    # Fetch news
    news_items = fetch_news()
    if not news_items:
        return
    
    # Process each news item
    for news_item in news_items:
        # Generate multiple memes
        meme_paths = generate_memes(news_item['title'])
        if not meme_paths:
            continue
        
        # Save to JSON
        save_memes(news_item, meme_paths)
    
    # View results
    view_memes()

if __name__ == "__main__":
    print("🚀 Starting local test...")
    main()