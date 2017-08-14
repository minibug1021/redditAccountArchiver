import praw, sqlite3, sys, time
from tqdm import tqdm
timeNOW = time.time()

r = praw.Reddit(client_id='',
                     client_secret='',
		     user_agent='',
                     password='',
                     username='')

user = r.redditor(sys.argv[1])

print('Generating database...')
conn = sqlite3.connect('{}.db'.format(user))
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comments(permalink TEXT, subreddit TEXT, comment TEXT, score INTEGER, timestamp INTEGER, controversiality INTEGER, edited TEXT, score_hidden TEXT, gilded INTEGER, distinguished TEXT, author_flair_css_class TEXT, author_flair_text TEXT, comment_id TEXT)')

print('Creating ID list...')
comments = {}
for comment in user.comments.new(limit=1000):
        comments[comment.id] = comment
for comment in user.comments.top(limit=1000):
        comments[comment.id] = comment

print('Fetching pre-existing comments...')
existing_ids = []
c.execute("SELECT comment_id FROM comments")
for row in c.fetchall():
	existing_ids.append(row[0])

for item in existing_ids:
        del comments[item]

print('Starting archival with {} new comments to process...'.format(len(comments)))

for id, comment in tqdm(comments.items()):
        permalink = 'reddit.com/r/{}/comments/{}//{}'.format(comment.subreddit, comment.submission, comment)
        c.execute('INSERT INTO comments (permalink, subreddit, comment, score, timestamp, controversiality, edited, score_hidden, gilded, distinguished, author_flair_css_class, author_flair_text, comment_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(permalink, str(comment.subreddit), comment.body, comment.score, comment.created_utc, comment.controversiality, comment.edited, comment.score_hidden, comment.gilded, comment.distinguished, comment.author_flair_css_class, comment.author_flair_text, comment.id))
        
        conn.commit()

seconds = time.time()-timeNOW
m,s = divmod(seconds,60)
h,m = divmod(m, 60)
print('Finished archiving /u/{} in %d hours, %02d minutes, and %02d seconds'.format(user) % (h, m, s))


c.close()
conn.close()
