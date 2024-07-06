import json
import os

import requests
from flask import Flask, jsonify, request, send_from_directory

PREDICTION_SERVICE_URL = os.environ.get("PREDICTION_SERVICE_URL", "http://localhost:5001").rstrip("/")

app = Flask(__name__, static_folder="static", static_url_path="")


@app.route("/")
def root():
    return send_from_directory("static", "index.html")


@app.route("/stations")
def station():
    with open("static/stations_data.json") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/proxy/<path:url>")
def proxy(url):
    target_url = f"{PREDICTION_SERVICE_URL}/{url}"
    resp = requests.get(target_url, params=request.args)
    return (resp.content, resp.status_code, resp.headers.items())


if __name__ == "__main__":
    app.run()
