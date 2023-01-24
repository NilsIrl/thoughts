import os

from flask import Flask, Blueprint, request, render_template
#from flask_login import LoginManager

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
)

app.secret_key = "asdlkfajfsdjffsdlkjdsfkljl"

#db = SQLAlchemy(app)
#login_manager = LoginManager()
#login_manager.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")
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
