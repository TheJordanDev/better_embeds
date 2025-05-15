from objects import ViewsData

def generate_html(v: ViewsData, _host:str="") -> str:
	host = "https://"+_host
	def meta_tag(attr, name, content):
		return f'<meta {attr}="{name}" content="{content}">\n'

	def og_tag(property, content):
		return f'<meta property="{property}" content="{content}">\n'

	def link_tag(rel, href, type_, title):
		return f'<link rel="{rel}" href="{href}" type="{type_}" title="{title}">\n'

	html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
	<meta charset="utf-8">
	<meta name="theme-color" content="#CE0071">
"""
	if not v.Error:
		if v.Card:
			html += meta_tag("name", "twitter:card", v.Card)
		if v.Title:
			html += meta_tag("name", "twitter:title", v.Title)
		if v.ImageURL:
			html += meta_tag("name", "twitter:image", v.ImageURL)
		if v.VideoURL:
			html += meta_tag("name", "twitter:player:width", v.Width)
			html += meta_tag("name", "twitter:player:height", v.Height)
			html += meta_tag("name", "twitter:player:stream", host+v.VideoURL)
			html += meta_tag("name", "twitter:player:stream:content_type", "video/mp4")
		if v.VideoURL or v.ImageURL:
			html += og_tag("og:site_name", "InstaJordan")
		html += og_tag("og:url", v.URL)
		html += og_tag("og:description", v.Description)
		if v.ImageURL:
			html += og_tag("og:image", host+v.ImageURL)
		if v.VideoURL:
			html += og_tag("og:video", host+v.VideoURL)
			html += og_tag("og:video:secure_url", host+v.VideoURL)
			html += og_tag("og:video:type", "video/mp4")
			html += og_tag("og:video:width", v.Width)
			html += og_tag("og:video:height", v.Height)
		if v.OEmbedURL:
			html += link_tag("alternate", v.OEmbedURL, "application/json+oembed", v.Title)
	else:
		html += meta_tag("name", "twitter:card", "summary")
		html += meta_tag("name", "twitter:title", "InstaJordan")
		html += meta_tag("name", "twitter:description", v.Error)
		# html += f'<meta http-equiv="refresh" content="0; url={v.URL}">\n'
	html += f"""    <title>Instagram Post</title>
  </head>
  <body>
	Redirecting you to the post in a moment.
	<a href="{v.URL}">Or click here.</a>
  </body>
</html>
"""
	return html