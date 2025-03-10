import json

f = open('comments.txt')
comments_raw = f.read().strip()

f2 = open('our_comments.json', 'w')

comment_objs = []
for comment in comments_raw.split(';'):
    comment_objs.append({'text': comment.strip()})

json.dump(comment_objs, f2, indent=4)
