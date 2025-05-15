from middlewares._middleware import Middleware
import math
import networkx as nx
from PIL import Image
import os, io, aiofiles, aiohttp, asyncio
from utils import getData
from flask import Response

# This module is intended to provide grid layout logic for Instagram images.
# The Go code provided describes an algorithm for arranging images in a grid
# with optimal row heights. The following is a Python adaptation of the core logic.


def avg(numbers):
	return sum(numbers) / len(numbers) if numbers else 0

def get_height(images_wh, canvas_width):
	total_aspect = sum(w / h for w, h in images_wh)
	if total_aspect == 0: return 0
	return canvas_width / total_aspect

def cost_fn(images_wh, i, j, canvas_width, max_row_height):
	slices = images_wh[i:j]
	row_height = get_height(slices, canvas_width)
	return (max_row_height - row_height) ** 2

def create_graph(images_wh, start, canvas_width, max_row_height=1000):
	results = {}
	for i in range(start + 1, min(len(images_wh) + 1, start + 4)):
		results[i] = cost_fn(images_wh, start, i, canvas_width, max_row_height)
	return results

def generate_grid(images):
	images_wh = [(im.width, im.height) for im in images]
	if not images_wh:
		return None

	all_width = [w for w, h in images_wh]
	canvas_width = int(avg(all_width) * 1.5)

	# Build graph for shortest path
	G = nx.DiGraph()
	for i in range(len(images_wh) + 1):
		edges = create_graph(images_wh, i, canvas_width)
		for j, cost in edges.items():
			G.add_edge(i, j, weight=cost)

	try:
		path = nx.shortest_path(G, 0, len(images_wh), weight='weight')
	except nx.NetworkXNoPath:
		return None

	height_rows = []
	canvas_height = 0
	for i in range(1, len(path)):
		row_wh = images_wh[path[i-1]:path[i]]
		row_height = int(get_height(row_wh, canvas_width))
		height_rows.append(row_height)
		canvas_height += row_height

	canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))

	y_offset = 0
	for i in range(1, len(path)):
		in_row = images[path[i-1]:path[i]]
		row_height = height_rows[i-1]
		x_offset = 0
		for img in in_row:
			new_width = int(row_height * img.width / img.height)
			resized = img.resize((new_width, row_height), Image.LANCZOS)
			canvas.paste(resized, (x_offset, y_offset))
			x_offset += new_width
		y_offset += row_height

	return canvas

class GridMiddleware(Middleware):
	postID: str
	def __init__(self, postID):
		self.postID = postID

	async def process(self):
		import logging
		logging.info("Grid processing for postID: %s", self.postID)
		grid_fname = os.path.join("static", f"{self.postID}.jpeg")

		# Return from cache if exists
		if os.path.exists(grid_fname):
			data = None
			async with aiofiles.open(grid_fname, "rb") as f:
				data = await f.read()
			if data:
				return Response(data, mimetype="image/jpeg", headers={"Content-Disposition": f"inline; filename={self.postID}.jpeg"})
		# Fetch post data (assume get_post_data is implemented elsewhere)
		item = await getData(self.postID)
		if not item or not hasattr(item, "Medias"):
			return None

		# Only include images
		media_urls = [m.URL for m in item.Medias if "Image" in getattr(m, "TypeName", getattr(m, "TypeName", ""))]

		if len(item.Medias) == 1 or len(media_urls) == 1:
			# Redirect logic would be handled at the route/controller level
			return None

		# Download images asynchronously

		async def fetch_image(session, url):
			try:
				async with session.get(url) as resp:
					if resp.status == 200:
						data = await resp.read()
						return Image.open(io.BytesIO(data)).convert("RGB")
			except Exception:
				return None

		async with aiohttp.ClientSession() as session:
			tasks = [fetch_image(session, url) for url in media_urls]
			images = [img for img in await asyncio.gather(*tasks) if img]

		if not images:
			return None

		grid_img = generate_grid(images)
		if grid_img is None:
			return None

		os.makedirs(os.path.dirname(grid_fname), exist_ok=True)
		buf = io.BytesIO()
		grid_img.save(buf, format="JPEG", quality=80)
		buf.seek(0)
		data = buf.read()
		return Response(data, mimetype="image/jpeg", headers={"Content-Disposition": f"inline; filename={self.postID}.jpeg"})