from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Use environment variable for safety
API_TOKEN = os.environ.get("CR_API_TOKEN")  # Set this in Render Dashboard

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

@app.route("/get-deck", methods=["POST"])
def get_deck():
    try:
        data = request.get_json()
        medals = int(data.get('medals'))

        # Step 1: Get leaderboard players
        leaderboard_url = "https://api.clashroyale.com/v1/rankings/global/players"
        res = requests.get(leaderboard_url, headers=HEADERS)

        if res.status_code != 200:
            return jsonify({"error": "Leaderboard fetch failed"}), 500

        players = res.json().get("items", [])

        # Step 2: Match exact medals and fetch deck
        for player in players:
            if player.get("trophies") == medals:
                tag = player["tag"].replace("#", "%23")
                battle_url = f"https://api.clashroyale.com/v1/players/{tag}/battlelog"
                battle_res = requests.get(battle_url, headers=HEADERS)

                if battle_res.status_code != 200:
                    return jsonify({"error": "Battle log fetch failed"}), 500

                battles = battle_res.json()
                for battle in battles:
                    if battle["type"] == "PvP":
                        deck = [{"name": c["name"], "level": c["level"]} for c in battle["team"][0]["cards"]]
                        return jsonify({"deck": deck})

        return jsonify({"error": "Player not found with exact medals"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Backend is Running"

if __name__ == "__main__":
    app.run()
