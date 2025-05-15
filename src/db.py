import sqlite3
import json
from datetime import datetime, timezone
from objects import DBPost

DB_PATH = "embeds.db"

def init_db():
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("""
		CREATE TABLE IF NOT EXISTS posts (
			postId TEXT PRIMARY KEY,
			username TEXT NOT NULL,
			caption TEXT,
			medias TEXT NOT NULL,
			created_at TEXT NOT NULL
		)
	""")
	conn.commit()
	conn.close()

def insert_post_obj(post:DBPost):
	if post.created_at is None:
		post.created_at = datetime.now(timezone.utc).isoformat()
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("""
		INSERT INTO posts (postId, username, caption, medias, created_at)
		VALUES (?, ?, ?, ?, ?)
	""", (post.postId, post.username, post.caption, post.medias, post.created_at))
	conn.commit()
	conn.close()

def insert_post(postId, username, caption, medias, created_at=None):
	if created_at is None:
		created_at = datetime.now(timezone.utc).isoformat()
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("""
		INSERT INTO posts (postId, username, caption, medias, created_at)
		VALUES (?, ?, ?, ?, ?)
	""", (postId, username, caption, medias, created_at))
	conn.commit()
	conn.close()

def get_post(postId):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("SELECT postId, username, caption, medias, created_at FROM posts WHERE postId = ?", (postId,))
	row = c.fetchone()
	conn.close()
	if row:
		return DBPost(
			postId=row[0],
			username=row[1],
			caption=row[2],
			medias=row[3],
			created_at=row[4]
		)
	return None

def has_post(postId):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute("SELECT 1 FROM posts WHERE postId = ?", (postId,))
	exists = c.fetchone() is not None
	conn.close()
	return exists

# Example usage:
if __name__ == "__main__":
	init_db()