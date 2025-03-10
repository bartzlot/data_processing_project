import requests
import json
from urllib.parse import urlparse, parse_qsl
from get_config import load_config
from datetime import datetime
import re
import os

class YouTubeCommentsFetcher:
    BASE_URL = 'https://www.googleapis.com/youtube/v3/commentThreads'

    def __init__(self, api_key: str):
        """
        Initialize the YouTubeCommentsFetcher with an API key.
        :param api_key: YouTube API key
        """
        self.api_key = api_key

    @staticmethod
    def strip_emojis(text: str) -> str:
        """Remove all emojis from a given text string using regex."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & pictographs
            "\U0001F680-\U0001F6FF"  # Transport & map symbols
            "\U0001F700-\U0001F77F"  # Alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric symbols
            "\U0001F800-\U0001F8FF"  # Supplemental symbols
            "\U0001F900-\U0001F9FF"  # Supplemental symbols and pictographs
            "\U0001FA00-\U0001FA6F"  # Chess pieces, symbols
            "\U0001FA70-\U0001FAFF"  # More symbols
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed characters
            "]+",
            flags=re.UNICODE
        )
    
        return emoji_pattern.sub('', text)

    @staticmethod
    def extract_video_id(video_url: str) -> str:
        """
        Extracts YouTube video ID from a given URL.
        :param video_url: YouTube video URL
        :return: Video ID as a string
        """
        parsed = urlparse(video_url)
        if parsed.netloc == 'youtu.be':
            return parsed.path.lstrip('/')
        query_params = dict(parse_qsl(parsed.query))
        return query_params.get('v', '')

    def fetch_comments(self, video_id: str, max_results: int = 10) -> list:
        """
        Fetches a list of comments and like counts for a given video ID.
        :param video_id: YouTube video ID
        :param max_results: Maximum number of comments to retrieve
        :return: List of comments with like count
        """
        comments = []
        next_page_token = None

        while len(comments) < max_results:

            results_to_fetch = min(max_results - len(comments), 100)
            params = {
                'key': self.api_key,
                'textFormat': 'plainText',
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': results_to_fetch,
                'pageToken': next_page_token,
                'order': 'relevance'
            }

            response = requests.get(self.BASE_URL, params=params)

            if response.status_code != 200:
                print(f'Error while fetching comments: {response.status_code}')
                break

            data = response.json()
            next_page_token = data.get('nextPageToken')

            for item in data.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                strip_text = YouTubeCommentsFetcher.strip_emojis(snippet['textDisplay'])
                comments.append({'text': strip_text, 'likes': snippet['likeCount']})

            if not next_page_token:
                break

        return comments
    

    @staticmethod
    def save_comments_to_json(comments: list):
        """
        Saves the fetched comments to a JSON file with a timestamp.
        
        :param comments: List of comments
        """

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"comments_{current_time}.json"
        save_path = os.path.join(os.path.dirname(__file__), "..", "output", "comments", file_name)

        try:

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'w', encoding='utf-8') as file:
                json.dump(comments, file, indent=4, ensure_ascii=False)

            print(f'Comments saved to {save_path}')
        except Exception as e:
            print(f' Error while saving comments to JSON: {e}')


if __name__ == '__main__':

    API_KEYS = load_config()
    comments_fetcher = YouTubeCommentsFetcher(API_KEYS['YT_API_KEY'])
    video_id = YouTubeCommentsFetcher.extract_video_id('https://www.youtube.com/watch?v=64_Msnda8ZU')
    comments = comments_fetcher.fetch_comments(video_id, max_results=100)
    YouTubeCommentsFetcher.save_comments_to_json(comments)

    

