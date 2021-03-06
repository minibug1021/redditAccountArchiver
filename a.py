#!/usr/bin/env python3

import praw, sqlite3, sys, time, winsound
from tqdm import tqdm
from prawcore.exceptions import NotFound
timeNOW = time.time()

def print_no_newline(string):
    import sys
    sys.stdout.write(string)
    sys.stdout.flush()

r = praw.Reddit(client_id='',
                     client_secret='',
		     user_agent='',
                     password='',
                     username='')
#input from commandline
user = r.redditor(sys.argv[1])

try:
        does_exist = user.link_karma
except NotFound:
		print("Account is unable to be accessed for any number of reasons (Deleted, doesn't exist, reddit is down, etc), Aborting archival.")
		winsound.Beep(2000,1000)
		sys.exit()
print('Generating comment database...')
#creates db file with name of user
conn = sqlite3.connect('{}.db'.format(user))
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comments(permalink TEXT, subreddit TEXT, comment TEXT, score INTEGER, timestamp INTEGER, controversiality INTEGER, edited TEXT, score_hidden TEXT, gilded INTEGER, distinguished TEXT, author_flair_css_class TEXT, author_flair_text TEXT, comment_length INTEGER, comment_id TEXT)')


comments = {}
#adds the ID and comment object of the top 1k comments from Hot, New, etc. to our comments dict.

print('Creating ID list for new...')
for comment in user.comments.new(limit=1000):
                comments[comment.id] = comment

print('Creating ID list for hot...')
for comment in user.comments.hot(limit=1000):
        comments[comment.id] = comment

print_no_newline('Creating ID list for most controversial of... ')
def controversialCOMMENTS(time):
        print_no_newline(' {}...'.format(time))
        for comment in user.comments.controversial(time):
                comments[comment.id] = comment
				
def topCOMMENTS(time):
        print_no_newline(' {}...'.format(time))
        for comment in user.comments.top(time):
                comments[comment.id] = comment
				
times = ['hour','day','week','month','year','all']
for i in times:
        controversialCOMMENTS(i)
print('')
print_no_newline('Creating ID list for top of... ')
for i in times:
        topCOMMENTS(i)
print('')

update_scores = comments.copy()

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

#progress bar
for id, comment in tqdm(comments.items()):
        permalink = 'reddit.com/r/{}/comments/{}//{}'.format(comment.subreddit, comment.submission, comment)
        c.execute('INSERT INTO comments (permalink, subreddit, comment, score, timestamp, controversiality, edited, score_hidden, gilded, distinguished, author_flair_css_class, author_flair_text, comment_length, comment_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                  ,(permalink, str(comment.subreddit), comment.body, comment.score, comment.created_utc, comment.controversiality, comment.edited, comment.score_hidden, comment.gilded, comment.distinguished, comment.author_flair_css_class, comment.author_flair_text, len(comment.body), comment.id))
        conn.commit()

print('Updating comment scores...')
for id, comment in tqdm(update_scores.items()):
	c.execute("UPDATE comments SET score=? WHERE comment_id=?", (comment.score,id))
	conn.commit()
# ↑comments↑ --- ↓posts↓
        
print('\nGenerating post database...')
c.execute('CREATE TABLE IF NOT EXISTS posts(permalink TEXT, subreddit TEXT, title TEXT, body TEXT, link TEXT, domain TEXT, is_self TEXT, score INTEGER, timestamp INTEGER, edited TEXT, gilded INTEGER, distinguished TEXT, author_flair_css_class TEXT, author_flair_text TEXT, link_flair TEXT, body_length INTEGER, post_id TEXT)')

posts = {}

print('Creating ID list for new...')
for post in user.submissions.new(limit=1000):
        posts[post.id] = post

print('Creating ID list for hot...')
for post in user.submissions.hot(limit=1000):
        posts[post.id] = post

print_no_newline('Creating ID list for most controversial of... ')
def controversialPOSTS(time):
        print_no_newline(' {}...'.format(time))
        for post in user.submissions.controversial(time):
                posts[post.id] = post
def topPOSTS(time):
        print_no_newline(' {}...'.format(time))
        for post in user.submissions.top(time):
                posts[post.id] = post
				
for i in times:
        controversialPOSTS(i)
print('')
print_no_newline('Creating ID list for top of... ')
for i in times:
        topPOSTS(i)
print('')

update_posts = posts.copy()

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

print('Updating post scores...')
for id, post in tqdm(update_posts.items()):
	c.execute("UPDATE posts SET score=? WHERE post_id=?", (post.score,id))
	conn.commit()

#delete count tables if they already exist
#honestly its easier to just rebuild it every time than issue a trillion update statements
c.execute('DROP TABLE IF EXISTS countPosts')
c.execute('DROP TABLE IF EXISTS countComments')
c.execute('DROP TABLE IF EXISTS commentBreakdown')
c.execute('DROP TABLE IF EXISTS postsBreakdown')

#going to do the same thing for posts and comments.
#select the subs and totals with this, append it to a list, then add it to the main database in two new tables.
selected1 = c.execute('SELECT DISTINCT subreddit, SUM(score) AS karma, COUNT(subreddit) AS CountOf FROM comments GROUP BY subreddit ORDER BY subreddit ASC')
rows1 = []
for row in selected1:
    rows1.append(row)
c.execute('CREATE TABLE IF NOT EXISTS commentBreakdown(subreddit TEXT, Count INTEGER, Karma INTEGER)')
for i in rows1:
    c.execute('INSERT INTO commentBreakdown (subreddit, Count, Karma) VALUES (?,?,?)',(i[0],i[2],i[1]))
conn.commit()

selected2 = c.execute('SELECT DISTINCT subreddit, SUM(score) AS karma, COUNT(subreddit) AS CountOf FROM posts GROUP BY subreddit ORDER BY subreddit ASC')
rows2 = []
for row in selected2:
    rows2.append(row)
c.execute('CREATE TABLE IF NOT EXISTS postsBreakdown(subreddit TEXT, Count INTEGER, Karma INTEGER)')
for i in rows2:
    c.execute('INSERT INTO postsBreakdown (subreddit, Count, Karma) VALUES (?,?,?)',(i[0],i[2],i[1]))
conn.commit()
print('Finished making subreddit and post counts')

seconds = time.time()-timeNOW
m,s = divmod(seconds,60)
h,m = divmod(m, 60)
print('Finished archiving /u/{} in %d hours, %02d minutes, and %02d seconds'.format(user) % (h, m, s))


c.close()
conn.close()
