# redditAccountArchiver

Archives reddit accounts by taking the top 1k Newest, Popular, Controversial, and Top comments.

Also grabs every post it can find.

Must be run through command line, ala `master.py -a 'username'`

If run twice on the same username, it will add any new comments.

| Flag Purpose | Flag | Optional Parameters |
| ------------- | ------------- | ------------- |
| Archives an account. Second parameter after -a must be an account's name. | -a | |
| Updates all accounts in current directory. No additional parameters needed.  | -u  | |
| Archives the account of every commenter in a thread. Must be structured as `master.py -t thread_id`. If you add -n after the thread_id, it puts all the archived accounts into a new folder. | -t  | -n |

# Required libs

* praw4 or above

* tqdm 

* sqlite3
