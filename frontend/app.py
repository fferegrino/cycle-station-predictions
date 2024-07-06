import json

from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")


@app.route("/")
def root():
    return send_from_directory("static", "index.html")


@app.route("/stations")
def station():
    with open("static/stations_data.json") as f:
        data = json.load(f)
    return jsonify(data)


if __name__ == "__main__":
    app.run()
