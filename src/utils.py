import httpx
from objects import Media, InstaData
import logging
import re
import json
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from db import get_post, insert_post_obj, has_post

BASE_USER_HEADER = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

async def _scrapeFromEmbedHTML(body: str) -> str:
	soup = BeautifulSoup(body, "html.parser")

	# Determine media type and URL
	typename = "GraphImage"
	embed_media = soup.select_one(".EmbeddedMediaImage")
	if not embed_media:
		typename = "GraphVideo"
		embed_media = soup.select_one(".EmbeddedMediaVideo")
	media_url = embed_media["src"] if embed_media and embed_media.has_attr("src") else None
	if not media_url:
		return ""

	# Get username
	username_elem = soup.select_one(".UsernameText")
	username = username_elem.get_text(strip=True) if username_elem else ""

	# Remove caption comments and username from caption
	for elem in soup.select(".CaptionComments"):
		elem.decompose()
	for elem in soup.select(".CaptionUsername"):
		elem.decompose()
	caption_elem = soup.select_one(".Caption")
	caption = caption_elem.get_text("\n", strip=True) if caption_elem else ""

	# Check if contains WatchOnInstagram
	video_blocked = "true" if "WatchOnInstagram" in body else "false"

	# Escape caption for JSON
	def escape_json_string(s):
		return json.dumps(s)

	# Compose JSON string
	json_str = (
		'{'
		'"shortcode_media": {'
			'"owner": {"username": "' + username + '"},'
			'"node": {"__typename": "' + typename + '", "display_url": "' + media_url + '"},'
			'"edge_media_to_caption": {"edges": [{"node": {"text": ' + escape_json_string(caption) + '}}]},'
			'"dimensions": {"height": null, "width": null},'
			'"video_blocked": ' + video_blocked +
		'}'
		'}'
	)
	return json_str

async def _scrapeFromGQL(postId: str) -> str:
	import urllib.parse

	gql_params = {
		"av": "0",
		"__d": "www",
		"__user": "0",
		"__a": "1",
		"__req": "k",
		"__hs": "19888.HYP:instagram_web_pkg.2.1..0.0",
		"dpr": "2",
		"__ccg": "UNKNOWN",
		"__rev": "1014227545",
		"__s": "trbjos:n8dn55:yev1rm",
		"__hsi": "7380500578385702299",
		"__dyn": "7xeUjG1mxu1syUbFp40NonwgU7SbzEdF8aUco2qwJw5ux609vCwjE1xoswaq0yE6ucw5Mx62G5UswoEcE7O2l0Fwqo31w9a9wtUd8-U2zxe2GewGw9a362W2K0zK5o4q3y1Sx-0iS2Sq2-azo7u3C2u2J0bS1LwTwKG1pg2fwxyo6O1FwlEcUed6goK2O4UrAwCAxW6Uf9EObzVU8U",
		"__csr": "n2Yfg_5hcQAG5mPtfEzil8Wn-DpKGBXhdczlAhrK8uHBAGuKCJeCieLDyExenh68aQAKta8p8ShogKkF5yaUBqCpF9XHmmhoBXyBKbQp0HCwDjqoOepV8Tzk8xeXqAGFTVoCciGaCgvGUtVU-u5Vp801nrEkO0rC58xw41g0VW07ISyie2W1v7F0CwYwwwvEkw8K5cM0VC1dwdi0hCbc094w6MU1xE02lzw",
		"__comet_req": "7",
		"lsd": "AVoPBTXMX0Y",
		"jazoest": "2882",
		"__spin_r": "1014227545",
		"__spin_b": "trunk",
		"__spin_t": "1718406700",
		"fb_api_caller_class": "RelayModern",
		"fb_api_req_friendly_name": "PolarisPostActionLoadPostQueryQuery",
		"variables": json.dumps({
			"shortcode": postId,
			"fetch_comment_count": 40,
			"parent_comment_count": 24,
			"child_comment_count": 3,
			"fetch_like_count": 10,
			"fetch_tagged_user_count": None,
			"fetch_preview_comment_count": 2,
			"has_threaded_comments": True,
			"hoisted_comment_id": None,
			"hoisted_reply_id": None
		}),
		"server_timestamps": "true",
		"doc_id": "25531498899829322"
	}

	headers = {
		"Accept": "*/*",
		"Accept-Language": "en-US,en;q=0.9",
		"Content-Type": "application/x-www-form-urlencoded",
		"Origin": "https://www.instagram.com",
		"Priority": "u=1, i",
		"Sec-Ch-Prefers-Color-Scheme": "dark",
		"Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
		"Sec-Ch-Ua-Full-Version-List": '"Google Chrome";v="125.0.6422.142", "Chromium";v="125.0.6422.142", "Not.A/Brand";v="24.0.0.0"',
		"Sec-Ch-Ua-Mobile": "?0",
		"Sec-Ch-Ua-Model": '""',
		"Sec-Ch-Ua-Platform": '"macOS"',
		"Sec-Ch-Ua-Platform-Version": '"12.7.4"',
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
		"X-Asbd-Id": "129477",
		"X-Bloks-Version-Id": "e2004666934296f275a5c6b2c9477b63c80977c7cc0fd4b9867cb37e36092b68",
		"X-Fb-Friendly-Name": "PolarisPostActionLoadPostQueryQuery",
		"X-Ig-App-Id": "936619743392459"
	}

	data = urllib.parse.urlencode(gql_params)
	url = "https://www.instagram.com/graphql/query/"

	async with httpx.AsyncClient(timeout=15) as client:
		resp = await client.post(url, data=data, headers=headers)
		resp.raise_for_status()
		return resp.text

async def getData(postId) -> InstaData:
	if len(postId) == 0 or (postId[0] != 'C' and postId[0] != 'D' and postId[0] != 'B'):
		raise ValueError("postId is not a valid Instagram post ID")
	
	instaData = InstaData(post_id=postId)

	if has_post(postId):
		post = get_post(postId)
		if post:
			instaData.Username = post.username
			instaData.Caption = post.caption
			instaData.Medias = post._medias()
			return instaData

	timeSliceData = None

	url = instaData.get_scrape_url()

	async with httpx.AsyncClient() as client:
		client.headers.update(BASE_USER_HEADER)
		response = await client.get(url)
		if response.status_code != 200:
			raise ValueError("Failed to fetch data from Instagram")

		if (len(response.text) == 0):
			logging.warning(f"Failed to parse data from TimeSliceImpl: postID={instaData.PostID}, err=No data found")
			raise ValueError("No data found in Instagram response")

		lines = response.text.split('\n')
		script_text = None
		for line in lines:
			if "shortcode_media" in line:
				script_text = line
				break

		if script_text is None or len(script_text) == 0:
			logging.warning(f"Failed to parse data from TimeSliceImpl: postID={instaData.PostID}, err=No script found")
			raise ValueError("No script found in Instagram response")
		
		script_start = script_text.find('>')
		if script_start != -1:
			script_text = script_text[script_start + 1:]

		match = re.search(r's\.handle\(\s*({.*?})\s*\);\s*requireLazy', script_text, re.DOTALL)
		if match:
			json_str = match.group(1)
			data = json.loads(json_str)
			timeSliceData_str = data.get("require")[1][-1][0].get("contextJSON")
			timeSliceData = json.loads(timeSliceData_str).get("gql_data")
		else:
			logging.warning(f"Failed to parse data from TimeSliceImpl: postID={instaData.PostID}, err=No valid JSON found")
			raise ValueError("No valid JSON found in Instagram response")

		try:
			embed_html = await _scrapeFromEmbedHTML(response.text)
			if embed_html:
				embed_data = json.loads(embed_html)
			else:
				embed_data = None
		except Exception as err:
			logging.warning(f"Failed to parse data from scrapeFromEmbedHTML: postID={instaData.PostID}, err={err}")
			embed_data = None

		# Determine if video is blocked
		video_blocked = response.text.find("WatchOnInstagram") != -1

		# Scrape from GraphQL API only if video is blocked or embed data is empty
		gql_data = None
		if video_blocked or not embed_data:
			try:
				gql_value = await _scrapeFromGQL(instaData.PostID)
			except Exception as err:
				logging.error(f"Failed to scrape data from scrapeFromGQL: postID={instaData.PostID}, err={err}")
				gql_value = None
			if gql_value and "require_login" not in gql_value:
				try:
					gql_json = json.loads(gql_value)
					gql_data = gql_json.get("data")
					logging.info(f"Data parsed from GraphQL API: postID={instaData.PostID}")
				except Exception as err:
					logging.error(f"Failed to parse GraphQL data: postID={instaData.PostID}, err={err}")

		# If gql_data is empty, use timeSliceData or embed_data
		if not gql_data:
			if timeSliceData:
				gql_data = timeSliceData
			elif embed_data:
				gql_data = embed_data

		status = gql_data.get("status") if gql_data else None
		item = None
		if gql_data:
			item = gql_data.get("shortcode_media")
			if not item:
				item = gql_data.get("xdt_shortcode_media")
				if not item:
					if status == "fail":
						raise ValueError("scrapeFromGQL is blocked")
					raise ValueError("Instagram post not found")

		media_items = [item] if item else []
		if item and item.get("edge_sidecar_to_children"):
			media_items = item["edge_sidecar_to_children"].get("edges", [])

		# Get username
		instaData.Username = item.get("owner", {}).get("username") if item else None

		# Get caption
		caption = ""
		if item:
			edges = item.get("edge_media_to_caption", {}).get("edges", [])
			if edges and "node" in edges[0]:
				caption = edges[0]["node"].get("text", "")
		instaData.Caption = caption.strip()

		# Get medias
		medias = []
		for m in media_items:
			node = m.get("node") if m and "node" in m else m
			if not node: continue
			media_url = node.get("video_url") or node.get("display_url")
			if not media_url: continue
			medias.append(Media(
				type_name=node.get("__typename", ""),
				url=media_url
			))
		instaData.Medias = medias

		# Failed to scrape from Embed
		if not instaData.Medias:
			raise ValueError("No media found in Instagram post")

		# Save to database
		if not has_post(postId):
			insert_post_obj(instaData.to_db_post())
		return instaData
	
def mediaid_to_code(media_id: int) -> str:
	alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
	short_code = ""
	while media_id > 0:
		remainder = media_id % 64
		media_id //= 64
		short_code = alphabet[remainder] + short_code
	return short_code

async def get_share_post_id(post_id: str) -> str:
	url = f"https://www.instagram.com/share/reel/{post_id}/"
	async with httpx.AsyncClient(follow_redirects=False, timeout=10) as client:
		resp = await client.head(url, headers=BASE_USER_HEADER)
		location = resp.headers.get("Location")
		if not location:
			return post_id
		redir_path = urlparse(location).path
		resolved_id = os.path.basename(redir_path)
		if resolved_id == "login":
			raise ValueError("not logged in")
		return resolved_id