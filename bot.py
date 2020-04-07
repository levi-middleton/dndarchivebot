import praw
from pprint import pprint
import sqlite3
import logging.config
import json
import os
import datetime

def init_database():
	conn = sqlite3.connect('db.sqlite')
	conn.execute('CREATE TABLE IF NOT EXISTS migrations (filename TEXT PRIMARY KEY, run_date TEXT NOT NULL)')
	db = conn.cursor()
	for filename in sorted(os.listdir('migrations'),key=lambda f: int(''.join(filter(str.isdigit, f)))):
		if(not filename.endswith('.sql')):
			continue
		db.execute('SELECT COUNT(*) FROM migrations where filename = ?',(filename,))
		(number_of_rows,) = db.fetchone()
		if(number_of_rows != 0):
			continue
		logging.info('Running migration ' + filename)
		with open(os.path.join('migrations',filename)) as f:
			conn.execute(f.read())
		conn.execute('INSERT INTO migrations (filename, run_date) VALUES (?,?)',(filename, str(datetime.datetime.now())))
	return conn
	
def get_saved(r, db):
	accepted_subreddits = ['UnearthedArcana', 'DnD', 'DungeonsAndDragons', 'TheGriffonsSaddlebag', 'dungeondraft', 'mapmaking', 'Roll20', 'dndnext']
	counts = {}
	for item in r.user.me().saved(limit = None):
		display_name = item.subreddit.display_name
		if(display_name in accepted_subreddits):
			db.execute('SELECT COUNT(*) FROM submissions WHERE id = ?',(str(item.id),))
			(number_of_rows,) = db.fetchone()
			if(number_of_rows == 0):
				if(isinstance(item, praw.models.Comment)):
					title = 'Comment on ' + item.submission.title
					db.execute('INSERT INTO submissions(id,permalink,title) VALUES (?,?,?)', (str(item.id),'https://www.reddit.com' + str(item.permalink),title))
				else:
					db.execute('INSERT INTO submissions(id,permalink,title) VALUES (?,?,?)', (str(item.id),'https://www.reddit.com' + str(item.permalink),str(item.title)))
			if(display_name in counts):
				counts[display_name] = counts[display_name] + 1
			else:
				counts[display_name] = 1
			item.unsave()
	print(counts)
	return
	
def main():
	try:
		with open('log.conf') as f:
			logging.config.dictConfig(json.load(f))
		logging.info("Beginning script execution")
		conn = init_database()
		db = conn.cursor()
		r = praw.Reddit('bot1')
		logging.debug("Running bot with user " + str(r.user.me()))	
		
		get_saved(r,db)
		
		conn.commit()
		conn.close()
	except:
		logging.exception("Unexpected termination")

if __name__ == "__main__":
	main()
