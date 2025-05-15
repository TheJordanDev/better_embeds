from flask import Blueprint, request

from middlewares.instagram.embed import EmbedMiddleware
from middlewares.instagram.video import VideoMiddleware
from middlewares.instagram.image import ImageMiddleware
from middlewares.instagram.grid import GridMiddleware
from middlewares.instagram.oembed import OEmbedMiddleware

instagram = Blueprint('instagram', __name__)

@instagram.route('/tv/<postID>')
@instagram.route('/reel/<postID>')
@instagram.route('/reels/<postID>')
@instagram.route('/stories/<username>/<postID>')
@instagram.route('/p/<postID>')
@instagram.route('/p/<postID>/<mediaNum>')
@instagram.route('/<username>/p/<postID>')
@instagram.route('/<username>/p/<postID>/<mediaNum>')
@instagram.route('/<username>/reel/<postID>')
async def embed(postID=None, username=None, mediaNum=None):
    query_params = request.args.to_dict()
    query_headers = request.headers
    headers_dict = dict(query_headers.items())
    host = request.host
    request_uri = request.path
    return await EmbedMiddleware(postID=postID, username=username, mediaNum=mediaNum, params=query_params, header=headers_dict, host=host, request_uri=request_uri).process()

@instagram.route('/images/<postID>/<mediaNum>')
async def images(postID, mediaNum):
    return await ImageMiddleware(postID=postID, mediaNum=mediaNum).process()

@instagram.route('/videos/<postID>/<mediaNum>')
async def videos(postID, mediaNum):
    return await VideoMiddleware(postID=postID, mediaNum=mediaNum).process()
    

@instagram.route('/grid/<postID>')
async def grid(postID):
    return await GridMiddleware(postID=postID).process()

@instagram.route('/oembed')
async def oembed():
    query_params = request.args.to_dict()
    return await OEmbedMiddleware(query_params=query_params).process()