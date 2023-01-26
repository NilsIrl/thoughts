import os

from flask import Flask, Blueprint, request, render_template
import subprocess
from pathlib import Path
from hackathon import db

def render_timeline(post):
    post_content, author_email = post
    post_content = subprocess.run(["cmark-gfm"], stdout=subprocess.PIPE, input=post_content).stdout
    return post_content, author_email


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='None',
        DATABASE=os.path.join(app.instance_path, "hackathon.sqlite3")
    )

    if not Path(app.config.database).exists():
        db.init_db()

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)
    
    from . import api
    app.register_blueprint(api.bp)
    
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/drafting")
    def drafting():
        return render_template("drafting.html")

    @app.route("/timeline")
    def timeline():
        from . import db
        db = db.get_db()
        cur = db.cursor()
        cur.execute("SELECT PostContent, PosterEmail FROM post ORDER BY PostId")
        timeline = list(map(render_timeline, cur.fetchall()))

        return render_template("timeline.html", timeline=timeline)
    return app

"""
@api_bp.route("/user", methods=["POST"])
def create_user():
    user = request.get_json()
    same_username = User.query.filter_by(username=user["username"]).first()
    if same_username:
        return "User with same username already exists", 400
    db.session.add(

        User(
            username=user["username"], password=generate_password_hash(user["password"])
        )
    )
    db.session.commit()
    return "User created", CREATED


@app.route("/user", methods=["GET"])
@login_required
def logged_in():
    return "Success!!", 200

@app.route("/login", methods=["POST"])
def login():
    credentials = request.get_json()
    user = User.query.filter(User.username == credentials["username"]).first()
    if user and check_password_hash(user.password, credentials["password"]):
        login_user(user, remember=credentials["remember"])
        return "Login successful"
    return "Unauthorized", 401


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    # TODO: redirect to a webpage
    return "Logged out successfully", 200

@app.route("/poll/<int:poll_id>/comments", methods=["GET"])
def get_comments(poll_id):
    return jsonify(Poll.query.filter_by(id=poll_id).first().get_comments())


@app.route("/polls", methods=["GET"])
def get_polls():
    if current_user.is_authenticated:
        user = current_user.id
    else:
        user = None
    return jsonify([poll.get_poll(user) for poll in Poll.query.all()])


@api_bp.route("/poll/<id>", methods=["DELETE"])
def delete_poll(id):
    # @nils add check if current user is poll author.
    Poll.query.filter_by(id=id).delete()
    Choice.query.filter_by(poll_id=id).delete()
    db.session.commit()
    return "Data deleted!", 200


@api_bp.route("/poll/<id>", methods=["GET"])
def get_poll(id):
    if current_user.is_authenticated:
        user = current_user.id
    else:
        user = None
    return jsonify(Poll.query.filter_by(id=id).first().get_poll())
"""
