from hackathon.db import get_db
from flask import request

def get_token(email: str) -> str:
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT token FROM user WHERE email = ?", (email,))
    return cur.fetchone()[0]

def get_email(token: str) -> str:
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT email FROM user WHERE token = ?", (token,))
    return cur.fetchone()[0]

def get_email_from_nothing() -> str:
    token = request.cookies.get("token")
    assert token != None
    return get_email(token)

def email_exists(email):
    print(email)
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM user WHERE email = ?", (email,))
    count = cur.fetchone()[0]

    return count >= 1

def token_exists(token: str) -> bool:
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM user WHERE token = ?", (token,))
    return cur.fetchone()[0] > 0

def logged_in() -> bool:
    token = request.cookies.get("token")
    return token != None and token_exists(token)
