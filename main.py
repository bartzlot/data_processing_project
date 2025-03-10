import json
from yt_comments import *
from analysis import *
from hate_detection import classify_good_bad_comments
from censure import *
from config import SENTIMENT_MODEL, CENSORED_STR

if __name__ == '__main__':
    print('Youtube comment sentiment analyzer')
    print('Initializing...')
    model = SentimentModel(SENTIMENT_MODEL)
    user_input = input("Paste your YouTube link or JSON file: ")
    if user_input.lower().startswith('f '):
        filename = user_input.split(' ', 1)[1]
        with open(filename) as f:
            comments = json.load(f)
    else:
        video_id = get_video_id(user_input)
        comments = get_video_comments(video_id)
    good_comment_objs, bad_comment_objs = classify_good_bad_comments(comments)
    bad_comments = [comment_obj['text'] for comment_obj in bad_comment_objs]

    print('Unfiltered comments:')
    for comment_obj in good_comment_objs:
        print(comment_obj['text'])
        print('Likes:', comment_obj.get('likes', None))
        print()

    print()
    print('Sentiment analysis...')
    results = model.analyze_all(good_comment_objs, LIKES_COEFFICIENT)
    # print('Averages:')
    model.print_result(results)

    bad_processed = censor_useless_comments(bad_comments)
    to_delete = []
    to_reword = []
    for original_comment, comment in zip(bad_comments, bad_processed):
        if comment == CENSORED_STR:
            to_delete.append(original_comment)
        else:
            to_reword.append(original_comment)
    reworded = reword_bad_comments(to_reword)

    print()
    print('Deleted:')
    for deleted in to_delete:
        print(deleted)
    print()
    print('Reworded:')
    for original, edited in zip(to_reword, reworded):
        print('-----')
        print(edited)
        print('--- Original ---')
        print(original)
        print('-----')
        print()
