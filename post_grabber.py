import praw,sys,os

r = praw.Reddit(client_id='',
                     client_secret='',
		     user_agent='',
                     password='',
                     username='')
#input from commandline

submission = r.submission(id=sys.argv[1])

authors = []
submission.comments.replace_more(limit=0)
comment_queue = submission.comments[:]  # Seed with top-level
while comment_queue:
    comment = comment_queue.pop(0)
    if comment.author not in authors:
        if comment.author != None:
            authors.append(comment.author)
    comment_queue.extend(comment.replies)

print('{} unique authors logging'.format(len(authors)))
for i in authors:
    os.system('a.py {}'.format(i))
