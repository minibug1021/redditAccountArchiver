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

print('Generating database...')
#creates db file with name of user
conn = sqlite3.connect('{}.db'.format(user))
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comments(permalink TEXT, subreddit TEXT, comment TEXT, score INTEGER, timestamp INTEGER, controversiality INTEGER, edited TEXT, score_hidden TEXT, gilded INTEGER, distinguished TEXT, author_flair_css_class TEXT, author_flair_text TEXT, comment_id TEXT)')


comments = {}
#adds the ID and comment object of the top 1k comments from Hot and New to our comments dict.
#the commets dict will NEVER be larger than 2k
print('Creating ID list for new...')
for comment in user.comments.new(limit=1000):
        comments[comment.id] = comment
print('Creating ID list for top...')
for comment in user.comments.top(limit=1000):
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
        c.execute('INSERT INTO comments (permalink, subreddit, comment, score, timestamp, controversiality, edited, score_hidden, gilded, distinguished, author_flair_css_class, author_flair_text, comment_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(permalink, str(comment.subreddit), comment.body, comment.score, comment.created_utc, comment.controversiality, comment.edited, comment.score_hidden, comment.gilded, comment.distinguished, comment.author_flair_css_class, comment.author_flair_text, comment.id))
        
        conn.commit()

#tells you how long it took to finish
seconds = time.time()-timeNOW
m,s = divmod(seconds,60)
h,m = divmod(m, 60)
print('Finished archiving /u/{} in %d hours, %02d minutes, and %02d seconds'.format(user) % (h, m, s))


c.close()
conn.close()
