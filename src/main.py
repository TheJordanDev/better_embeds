from flask import Flask, request, redirect, jsonify
from blueprints.instagram import instagram

import logging

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more details
    format='%(asctime)s %(levelname)s %(message)s'
)


app = Flask(__name__)
app.register_blueprint(instagram, url_prefix='/instagram')

@app.before_request
def strip_trailing_slash_with_params():
    path = request.path
    if path != '/' and path.endswith('/') and not request.endpoint == 'static':
        # Only redirect if removing the slash doesn't change the endpoint
        new_path = path.rstrip('/')
        # Preserve query string
        if request.query_string:
            return redirect(new_path + '?' + request.query_string.decode(), code=301)
        else:
            return redirect(new_path, code=301)

@app.route('/')
def home():
    # Set content type and call views.Home logic here
    return "<html><body>Home</body></html>", 200, {'Content-Type': 'text/html; charset=utf-8'}

def main():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()