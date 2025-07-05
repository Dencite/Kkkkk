from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

API_TOKEN = os.getenv("CR_API_TOKEN", "YOUR_API_TOKEN_HERE")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_deck", methods=["POST"])
def get_deck():
    try:
        medals = int(request.json.get("medals"))
    except:
        return jsonify({"error": "Invalid medal input"}), 400

    url = "https://api.clashroyale.com/v1/locations/global/pathOfLegends/season/ultimateChampionRankings"
    res = requests.get(url, headers=HEADERS)
    players = res.json().get("items", [])

    if not players:
        return jsonify({"error": "Could not fetch player data"}), 500

    # Find player with closest UC medals
    closest_player = min(players, key=lambda p: abs(p["trophies"] - medals))
    tag = closest_player["tag"].replace("#", "%23")
    matched_medals = closest_player["trophies"]
    name = closest_player["name"]

    log_url = f"https://api.clashroyale.com/v1/players/{tag}/battlelog"
    log = requests.get(log_url, headers=HEADERS).json()

    for b in log:
        if "cards" in b.get("team", [{}])[0]:
            deck = b["team"][0]["cards"]
            return jsonify({
                "deck": [{
                    "name": c["name"],
                    "level": c["level"],
                    "icon": c["iconUrls"]["medium"]
                } for c in deck],
                "player": name,
                "matched_medals": matched_medals
            })

    return jsonify({"error": "Deck not found"}), 404
