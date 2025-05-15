from middlewares._middleware import Middleware
from utils import getData
from flask import redirect, Response

class ImageMiddleware(Middleware):
	postID: str
	mediaNum: str
	def __init__(self, postID, mediaNum):
		self.postID = postID
		self.mediaNum = mediaNum

	async def process(self):
		data = await getData(self.postID)

		if int(self.mediaNum) > len(data.Medias):
			return Response("Media not found", status=404)

		image_url = data.Medias[max(1, int(self.mediaNum)) - 1].URL
		return redirect(image_url, code=302)