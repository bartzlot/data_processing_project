import requests
import json
from urllib.parse import urlparse, parse_qsl
from config import YT_API_KEY


API_URL_FORMAT = \
    ('https://www.googleapis.com/youtube/v3/commentThreads'
     '?key={}&textFormat=plainText&part=snippet&videoId={}&maxResults={}&pageToken={}')


def get_video_id(video_url: str) -> str:
    '''
    Get YouTube video id from a given url
    :param video_url:
    :return:
    '''
    parsed = urlparse(video_url)
    if parsed.netloc == 'youtu.be':
        return parsed.path[1:]
    query_params = parse_qsl(parsed.query)
    return next(x[1] for x in query_params if x[0]=='v')


def get_video_comments(video_id: str, max_results: int=10) -> list:
    '''
    Get a list of comments with like count of a video given by id
    :param video_id:
    :param max_results:
    :return:
    '''
    comments = []
    next_page_token = ' '

    while next_page_token and (results_remained := max_results-len(comments)) > 0:
        if results_remained >= 100:
            results_to_fetch = 100
        else:
            results_to_fetch = results_remained

        req = requests.get(API_URL_FORMAT.format(
            YT_API_KEY, video_id, results_to_fetch, next_page_token), params = {
                'order': 'relevance'
            }
        )
        if req.status_code == 200:
            comment_data = json.loads(req.content)
            if 'nextPageToken' in comment_data:
                next_page_token = comment_data['nextPageToken']
            else:
                next_page_token = None
            for comment_item in comment_data['items']:
                comments.append({
                    'text': comment_item['snippet']['topLevelComment']['snippet']['textDisplay'],
                    'likes': comment_item['snippet']['topLevelComment']['snippet']['likeCount']
                })
        else:
            print('Error while downloading comments:', req.status_code)
            break
    return comments


if __name__ == '__main__':
    url_link = input("Paste your link: ")
    f = open('comments.json', 'w')
    json.dump(get_video_comments(get_video_id(url_link), max_results=100), f, indent=2)
    # print(json.dumps(get_video_comments(get_video_id(url_link)), indent=2))
    #print(json.dumps(get_video_comments('dQw4w9WgXcQ'), indent=2))
    #print(get_video_id('https://www.youtube.com/watch?si=4H9S0xrXe4f8NxkN&%3Bt=12&v=Ct6BUPvE2sM&feature=youtu.be'))
    #print(get_video_id('https://youtu.be/DZSS-FeSXhc?si=KNS2jQABfoxGoyas'))
