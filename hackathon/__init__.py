import os

from flask import Flask, Blueprint, make_response, redirect, request, render_template
import subprocess
from hackathon.db import init_app, get_db
from hackathon.utils import get_email, get_token, email_exists, logged_in, token_exists

def render_post(post):
    post_content, author_email, post_time = post
    # TODO: sus of this str.encode
    post_content = subprocess.run(["cmark-gfm"], stdout=subprocess.PIPE, input=str.encode(post_content)).stdout.decode()
    return post_content, author_email, post_time

def render_timeline():
    token = request.cookies.get("token")
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT PostContent, PosterEmail, strftime('%Y-%m-%d %H:%M', PostTime, 'unixepoch') FROM post JOIN follow ON followee = PosterEmail JOIN user ON email = follower WHERE token = ? ORDER BY PostId DESC", (token,))
    timeline = list(map(render_post, cur.fetchall()))

    return render_template("timeline.html", posts=timeline)

def follows(followee: str) -> str:
    token = request.cookies.get("token")
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM follow JOIN user ON email = follower WHERE token = ? AND followee = ?", (token, followee))
    return cur.fetchone()[0] >= 1

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='None',
        DATABASE=os.path.join(app.instance_path, "hackathon.sqlite3")
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    init_app(app)
    
    from . import api
    app.register_blueprint(api.bp)
    
    @app.route("/")
    def index():
        token = request.cookies.get('token')

        if token != None and token_exists(token):
            return render_timeline()
        else:
            resp = make_response(render_template("index.html"))
            resp.delete_cookie("token")
            return resp

    @app.route("/post")
    def drafting():
        if logged_in():
            return render_template("drafting.html")
        else:
            return redirect("/")

    @app.route("/disconnect")
    def disconnect():
        resp = redirect("/")
        resp.delete_cookie("token")
        return resp

    @app.route("/profile")
    def profile():
        if logged_in():
            token = request.cookies.get("token")
            assert token != None
            email = get_email(token)
            return redirect(f"/users/{email}")
        else:
            return redirect("/")

    @app.route("/users/<string:email>")
    def show_user(email):
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT PostContent, PosterEmail, strftime('%Y-%m-%d %H:%M', PostTime, 'unixepoch') FROM post WHERE PosterEmail = ? ORDER BY PostId", (email,))
        timeline = list(map(render_post, cur.fetchall()))

        cur.execute("SELECT COUNT(*) FROM follow WHERE follower = ?", (email,))
        following = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM follow WHERE followee = ?", (email,))
        followers = cur.fetchone()[0]

        return render_template("user.html", email=email, posts=timeline, logged_in=logged_in(), follows=follows(email), followers=followers, following=following)

    # TODO: remove this
    @app.route("/post2")
    def post2():
        return render_template("post.html")

    return app