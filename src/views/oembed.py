import json

def oembed() -> str:
    data = {
        "author_name": "",
        "author_url": "",
        "provider_name": "InstaJordan",
        "provider_url": "https://github.com/Wikidepia/InstaFix",
        "title": "Embed",
        "type": "rich",
        "version": "1.0"
    }
    return json.dumps(data, ensure_ascii=False)