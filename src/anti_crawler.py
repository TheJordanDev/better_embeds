# anti_crawler.py

KNOWN_BOTS = [
	b"bot",
	b"facebook",
	b"embed",
	b"got",
	b"firefox/92",
	b"firefox/38",
	b"curl",
	b"wget",
	b"go-http",
	b"yahoo",
	b"generator",
	b"whatsapp",
	b"preview",
	b"link",
	b"proxy",
	b"vkshare",
	b"images",
	b"analyzer",
	b"index",
	b"crawl",
	b"spider",
	b"python",
	b"cfnetwork",
	b"node",
	b"mastodon",
	b"http.rb",
]

def is_bot(user_agent: bytes) -> bool:
	"""
	Checks if the given user agent string matches any known bot signatures.

	Args:
		user_agent (bytes): The user agent string as bytes.

	Returns:
		bool: True if a known bot is detected, False otherwise.
	"""
	if isinstance(user_agent, bytes):
		ua = user_agent.lower()
	else:
		ua = user_agent.lower().encode()
	for bot in KNOWN_BOTS:
		if bot in ua:
			return True
	return False