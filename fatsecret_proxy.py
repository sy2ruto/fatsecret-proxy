from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# FatSecret API Credentials
CLIENT_ID = "73ad95cc82e54c969be697d5e0974608"
CLIENT_SECRET = "fff59bb3a27e49b4b4a4d1e505e5469f"

# 1. Access Token 발급 함수
def get_access_token():
    url = "https://oauth.fatsecret.com/connect/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "basic"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()["access_token"]

# 2. 음식 검색 API 프록시
@app.route("/search", methods=["GET"])
def search_food():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "검색어(query)가 필요합니다"}), 400

    token = get_access_token()
    url = "https://platform.fatsecret.com/rest/server.api"
    params = {
        "method": "foods.search",
        "search_expression": query,
        "format": "json"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers, params=params)
    return jsonify(response.json())

# 서버 시작
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 