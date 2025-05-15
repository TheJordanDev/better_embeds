from typing import List, Dict
import json
from datetime import datetime
import logging

class Media:
	def __init__(self, type_name: str, url: str):
		self.TypeName = type_name
		self.URL = url

	def to_dict(self):
		return {
			"type_name": self.TypeName,
			"url": self.URL
		}

class InstaData:
	def __init__(self, post_id:str = None, username:str = None, caption:str = None, medias:List[Media] = None):
		self.PostID = post_id
		self.Username = username
		self.Caption = caption
		self.Medias = medias

	def get_scrape_url(self):
		return f"https://www.instagram.com/p/{self.PostID}/embed/captioned/"
	
	def to_db_post(self) -> 'DBPost':
		return DBPost(
			postId=self.PostID,
			username=self.Username,
			caption=self.Caption,
			medias=json.dumps([media.to_dict() for media in self.Medias]) if self.Medias else "[]",
			created_at=datetime.now().isoformat()
		)

	def to_dict(self):
		return {
			"post_id": self.PostID,
			"username": self.Username,
			"caption": self.Caption,
			"medias": [media.to_dict() for media in self.Medias] if self.Medias else []
		}
	
class ViewsData:
	def __init__(self, Card="", Title="InstaFix", ImageURL="", VideoURL="", URL="", Description="", OEmbedURL="", Width=400, Height=400, Error=""):
		self.Card = Card
		self.Title = Title
		self.ImageURL = ImageURL
		self.VideoURL = VideoURL
		self.URL = URL
		self.Description = Description
		self.OEmbedURL = OEmbedURL
		self.Width = Width
		self.Height = Height
		self.Error = Error

class OEmbedData:
	def __init__(self, Text, URL):
		self.Text = Text
		self.URL = URL

class DBPost:
	def __init__(self, postId: str, username: str, caption: str, medias: str, created_at: str):
		self.postId = postId
		self.username = username
		self.caption = caption
		self.medias = medias
		self.created_at = created_at

	def _medias(self) -> list['Media']:
		if isinstance(self.medias, str):
			media_list = json.loads(self.medias)
			medias = []
			for _media in media_list:
				media_obj = Media(_media["type_name"], _media["url"])
				medias.append(media_obj)
			return medias
		return self.medias

	def to_datetime(self):
		return datetime.fromisoformat(self.created_at)

	def __repr__(self):
		return f"DBPost(postId={self.postId}, username={self.username}, caption={self.caption}, medias={self.medias}, created_at={self.created_at})"