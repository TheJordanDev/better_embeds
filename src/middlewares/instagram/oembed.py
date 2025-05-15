from middlewares._middleware import Middleware
from views.oembed import oembed
from flask import Response

class OEmbedMiddleware(Middleware):
	query_params: dict
	header: dict
	host: str
	def __init__(self, query_params=None):
		self.query_params = query_params if query_params else {}

	async def process(self) -> Response:
		response = Response(None, status=200)

		response.headers.add("Content-Type","application/json")

		data = oembed()
		response.set_data(data)
		return response