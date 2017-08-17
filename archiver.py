#!/usr/bin/env python3

import praw, sqlite3, sys, time
from tqdm import tqdm
timeNOW = time.time()

r = praw.Reddit(client_id='',
                     client_secret='',
		     user_agent='',
                     password='',
                     username='')
#input from commandline
user = r.redditor(sys.argv[1])

print('Generating comment database...')
#creates db file with name of user
conn = sqlite3.connect('{}.db'.format(user))
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comments(permalink TEXT, subreddit TEXT, comment TEXT, score INTEGER, timestamp INTEGER, controversiality INTEGER, edited TEXT, score_hidden TEXT, gilded INTEGER, distinguished TEXT, author_flair_css_class TEXT, author_flair_text TEXT, comment_length INTEGER, comment_id TEXT)')

comments = {}
#adds the ID and comment object of the top 1k comments from Hot, New, and Controversial to our comments dict.
#the comments dict will NEVER be larger than 3k
print('Creating ID list for new...')
for comment in user.comments.new(limit=1000):
        comments[comment.id] = comment
print('Creating ID list for top...')
for comment in user.comments.top(limit=1000):
        comments[comment.id] = comment
print('Creating ID list for controversial...')
for comment in user.comments.controversial('all'):
        comments[comment.id] = comment


print('Fetching pre-existing comments...')
#adds already existing comments to a list so they can be filtered out
existing_ids = []
c.execute("SELECT comment_id FROM comments")
for row in c.fetchall():
	existing_ids.append(row[0])

#removes already existing comment IDs from our dict.
#the except is for when we have to deal with a deleted comment.
for item in existing_ids:
        try:
                del comments[item]
        except KeyError:
                pass

print('Starting archival with {} new comments to process...'.format(len(comments)))

#not so ghetto progress bar
for id, comment in tqdm(comments.items()):
        permalink = 'reddit.com/r/{}/comments/{}//{}'.format(comment.subreddit, comment.submission, comment)
        c.execute('INSERT INTO comments (permalink, subreddit, comment, score, timestamp, controversiality, edited, score_hidden, gilded, distinguished, author_flair_css_class, author_flair_text, comment_length, comment_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                  ,(permalink, str(comment.subreddit), comment.body, comment.score, comment.created_utc, comment.controversiality, comment.edited, comment.score_hidden, comment.gilded, comment.distinguished, comment.author_flair_css_class, comment.author_flair_text, len(comment.body), comment.id))
        conn.commit()
        
# ↑comments↑ --- ↓posts↓
        
print('\nGenerating post database...')
c.execute('CREATE TABLE IF NOT EXISTS posts(permalink TEXT, subreddit TEXT, title TEXT, body TEXT, link TEXT, domain TEXT, is_self TEXT, score INTEGER, timestamp INTEGER, edited TEXT, gilded INTEGER, distinguished TEXT, author_flair_css_class TEXT, author_flair_text TEXT, link_flair TEXT, body_length INTEGER, post_id TEXT)')

posts = {}

print('Creating ID list for new...')
for post in user.submissions.new(limit=1000):
        posts[post.id] = post

print('Creating ID list for top...')
for post in user.submissions.top(limit=1000):
        posts[post.id] = post
	
print('Creating ID list for controversial...')
for post in user.submissions.controversial('all'):
        posts[post.id] = post

print('Fetching pre-existing posts...')
existing_ids = []
c.execute("SELECT post_id FROM posts")
for row in c.fetchall():
	existing_ids.append(row[0])

for item in existing_ids:
        try:
                del posts[item]
        except KeyError:
                pass

print('Starting archival with {} new posts to process...'.format(len(posts)))

for id, post in tqdm(posts.items()):
        permalink = 'redd.it/{}'.format(post.id)
        c.execute('INSERT INTO posts (permalink, subreddit, title, body, link, domain, is_self, score, timestamp, edited, gilded, distinguished, author_flair_css_class, author_flair_text, link_flair, body_length, post_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                  ,(permalink, str(post.subreddit), str(post.title), post.selftext, post.url, post.domain, post.is_self, post.score, post.created_utc, post.edited, post.gilded, post.distinguished, post.author_flair_css_class, post.author_flair_text, post.link_flair_text, len(post.selftext), post.id))
        conn.commit()

seconds = time.time()-timeNOW
m,s = divmod(seconds,60)
h,m = divmod(m, 60)
print('Finished archiving /u/{} in %d hours, %02d minutes, and %02d seconds'.format(user) % (h, m, s))


c.close()
conn.close()
