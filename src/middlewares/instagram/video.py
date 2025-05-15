from middlewares._middleware import Middleware
from utils import getData
from flask import redirect, request


VideoProxyAddr:str = ""

class VideoMiddleware(Middleware):
	postID: str
	mediaNum: str
	def __init__(self, postID="", mediaNum=0):
		self.postID = postID
		self.mediaNum = mediaNum

	async def process(self):
		data = await getData(self.postID)
		try:
			media_num = max(1, int(self.mediaNum))
		except ValueError:
			return "Invalid media number", 500

		if media_num > len(data.Medias):
			return "Media number out of range", 404

		video_url = data.Medias[media_num - 1].URL
		if not video_url:
			return "Video URL not found", 404


		user_agent = request.headers.get("User-Agent", "")
		if "TelegramBot" in user_agent:
			return redirect(video_url, code=302)
		else:
			return redirect(VideoProxyAddr + video_url, code=302)
		
		