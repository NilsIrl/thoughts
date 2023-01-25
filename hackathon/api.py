from flask import Blueprint, jsonify, request
import requests
from hackathon.db import get_db

bp=Blueprint("api", __name__, url_prefix="/api")

VANA_LOGIN_URL = "https://api.vana.com/api/v0/auth/login"

@bp.route('/login')
def login():
    db = get_db()
    email = request.args.get("email")
    code = request.args.get("code")
    body = {
        "email": email,
        "code": code,
    }
    login_response = requests.post(VANA_LOGIN_URL, json=body)
    login_json_response = login_response.json()
    if login_json_response["success"]:
        token = login_json_response["token"]
        db.execute("INSERT INTO user(email, token) VALUES (?, ?)", (email, token))
        db.commit()
    
    return jsonify(login_json_response)