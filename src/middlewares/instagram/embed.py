from flask import redirect, Response
from middlewares._middleware import Middleware
from views.embed import ViewsData, generate_html
from utils import mediaid_to_code, get_share_post_id, getData
from anti_crawler import is_bot
from urllib.parse import quote
import logging

class EmbedMiddleware(Middleware):
	postID: str
	username: str
	mediaNum: str
	params: dict
	header: dict
	host: str
	request_uri: str

	def __init__(self, postID=None, username=None, mediaNum=None, params=None, header=None, host=None, request_uri=None):
		self.postID = postID
		self.username = username
		self.params = params if params else {}
		self.header = header if header else {}
		self.host = host if host else "localhost"
		self.mediaNum = mediaNum if mediaNum else self.params.get("img_index", 0)
		self.request_uri = request_uri if request_uri else self.params.get("request_uri", "")

	async def process(self) -> Response:
		is_direct = bool(self.params.get("direct", False))
		is_gallery = bool(self.params.get("gallery", False))

		embed_type = self.header.get("X-Embed-Type", "").lower()
		if embed_type == "direct":
			is_direct = True
		elif embed_type == "gallery":
			is_gallery = True

		if "/stories/" in self.params.get("path", ""):
			try:
				media_id = int(self.postID)
				self.postID = mediaid_to_code(media_id)
			except (ValueError, TypeError):
				views_data = ViewsData()
				views_data.Description = "Invalid postID"
				return generate_html(views_data, _host=self.host)
		elif "/share/" in self.params.get("path", ""):
			try:
				self.postID = await get_share_post_id(self.postID)
			except Exception:
				if not self.params.get("remote_scraper_addr"):
					views_data = ViewsData()
					views_data.Description = "Failed to get new postID from share URL"
					return generate_html(views_data, _host=self.host)
				
		views_data = ViewsData()
		views_data.Title = "InstaJordan"
		media_num_param = str(self.mediaNum)
		request_uri = self.request_uri
		views_data.URL = "https://instagram.com" + request_uri.replace("/" + media_num_param, "", 1)

		user_agent = self.header.get("User-Agent", "")
		if not is_bot(user_agent) and "debug" not in self.params.keys():
			return redirect(location=views_data.URL, code=302)

		try:
			item = await getData(self.postID)
		except Exception as e:
			logging.info(e)
			views_data.Error = str(e)
			return generate_html(views_data, _host=self.host)


		if not item or not getattr(item, "Medias", []):
			return redirect(location=views_data.URL, code=302)

		if int(self.mediaNum) >= len(item.Medias):
			views_data.Description = "Media number out of range"
			return generate_html(views_data, _host=self.host)
		elif not getattr(item, "Username", ""):
			views_data.Description = "Post not found"
			return generate_html(views_data, _host=self.host)
		
		views_data.Title = f"@{item.Username}"

		if not is_gallery:
			views_data.Description = getattr(item, "Caption", "")
			if len(views_data.Description) > 255:
				views_data.Description = views_data.Description[:250] + "..."

		media_index = max(1, int(self.mediaNum)) - 1
		typename = getattr(item.Medias[media_index], "TypeName", "")
		with open("type_name.txt", "a") as f:
			f.write(f"{typename}\n")
		is_image = "Image" in typename or "StoryVideo" in typename

		logging.info(len(item.Medias))
		if is_image and len(item.Medias) > 1:
			views_data.Card = "summary_large_image"
			views_data.ImageURL = f"/instagram/grid/{self.postID}"
		elif is_image:
			views_data.Card = "summary_large_image"
			views_data.ImageURL = f"/instagram/images/{self.postID}/{max(1, int(self.mediaNum))}"
		else:
			views_data.Card = "player"
			views_data.VideoURL = f"/instagram/videos/{self.postID}/{max(1, int(self.mediaNum))}"
			scheme = "https"
			host = self.host
			desc = quote(views_data.Description or "")
			url = quote(views_data.URL or "")
			views_data.OEmbedURL = f"{scheme}://{host}/instagram/oembed?text={desc}&url={url}"

		if is_direct:
			target_url = views_data.ImageURL if is_image else views_data.VideoURL
			return redirect(location=target_url, code=302)

		return generate_html(views_data, _host=self.host)