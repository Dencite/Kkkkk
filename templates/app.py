from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)
API_TOKEN = os.getenv("CR_API_TOKEN", "YOUR_API_TOKEN_HERE")
HEADERS = {"Authorization": f"Bearer " + API_TOKEN}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_deck", methods=["POST"])
def get_deck():
    medals = int(request.json.get("medals"))
    url = "https://api.clashroyale.com/v1/locations/global/pathOfLegends/season/ultimateChampionRankings"
    res = requests.get(url, headers=HEADERS)
    players = res.json().get("items", [])
    tag = next((p["tag"] for p in players if p["trophies"] == medals), None)
    if not tag:
        return jsonify({"error": "Player not found."}), 404

    tag = tag.replace("#", "%23")
    log_url = f"https://api.clashroyale.com/v1/players/{tag}/battlelog"
    log = requests.get(log_url, headers=HEADERS).json()
    for b in log:
        if "cards" in b.get("team", [{}])[0]:
            deck = b["team"][0]["cards"]
            return jsonify({"deck": [{
                "name": c["name"],
                "level": c["level"],
                "icon": c["iconUrls"]["medium"]
            } for c in deck]})
    return jsonify({"error": "Deck not found."}), 404o
