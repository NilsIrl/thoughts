from flask import Blueprint, jsonify, request, Response
import requests
import re
from hackathon.db import get_db
from hackathon.utils import get_token, get_email, email_exists
import time
import itertools

bp=Blueprint("api", __name__, url_prefix="/api")

VANA_LOGIN_URL = "https://api.vana.com/api/v0/auth/login"
VANA_GENERATION_URL_SYNC = "https://api.vana.com/api/v0/images/generations"
VANA_GENERATION_URL_ASYNC = "https://api.vana.com/api/v0/jobs/text-to-image"
VANA_GET_EXHIBIT_URL = "https://api.vana.com/api/v0/account/exhibits"

def vana_exhibit_url_for_id(id: int) -> str:
    return f"{VANA_GET_EXHIBIT_URL}/thoughts_{id}"

EMAIL_PATTERN = re.compile(r"@(\w+@\w+\.\w+)")

# Abstract class (TM)
class InvalidPromptError(Exception):
    pass

class NoEmailInvalidPromptError(InvalidPromptError):
    pass

class MultipleEmailInvalidPromptError(InvalidPromptError):
    pass

# returns the prompt followed by the email of the person in question
# parse_prompt replaces the uses of the person in the prompt
# parse_prompt may raise 2 different errors
# NoEmailInvalidPromptError in cases where there are no emailed @ed in the prompt (i.e. probably mistyped the email address)
# MultipleEmailInvalidPromptError when there are multiple different emails being used
def parse_prompt(prompt: str) -> tuple[str, str]:

    email_matches = filter(lambda email_match: email_exists(email_match.group(1)), EMAIL_PATTERN.finditer(prompt))
    try:
        first_email = next(email_matches)
    except StopIteration as exc:
        raise NoEmailInvalidPromptError() from exc
    
    final_prompt = prompt[:first_email.start(0)] + "{target_token}"
    end_of_previous = first_email.end(0) + 1

    for email_match in email_matches:
        if email_match.group(1) != first_email:
            raise MultipleEmailInvalidPromptError()
        final_prompt += prompt[end_of_previous:email_match.start(0)] + "{target_token}"
        end_of_previous = email_match.end(0) + 1

    final_prompt += prompt[end_of_previous:]

    return final_prompt, first_email.group(1)

@bp.route('/login')
def login():
    # TODO NOT-URGENT NOT-IMPORTANT: we may want to normalise the email
    # addresses to prevent duplicates (case sensitivity (or lack thereof))
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
        db.execute("INSERT OR REPLACE INTO user(email, token) VALUES (?, ?)", (email, token))

        db.execute("INSERT OR REPLACE INTO follow(follower, followee) VALUES (?, ?)", (email, email))
        db.commit()
    
    return jsonify(login_json_response)

@bp.route("/user_exists")
def user_exists():
    user_email = request.args.get("email")
    return jsonify(email_exists(user_email))

# Synchronous API exposed to browser
# It may be implemented using the vana sync or async API
@bp.route("/images", methods = ["POST"])
def generate_images():
    db = get_db()
    cur = db.cursor()
    prompt = request.args.get("prompt")

    assert prompt != None
    
    cur.execute("SELECT COUNT(*) FROM exhibit WHERE prompt = ?", (prompt,))
    if cur.fetchone()[0] > 0:
        while True:
            print("polling database for images for prompt:", prompt)
            cur.execute("SELECT imageUrl FROM image JOIN exhibit ON exhibit_id = ExhibitId WHERE prompt = ?", (prompt,))
            image_urls = cur.fetchall()
            if len(image_urls) > 0:
                return jsonify(list(map(lambda row: row[0], image_urls)))
            # TODO IMPORTANT does this block?
            time.sleep(5)
    
    # TODO actually do this properly REGEX WORD BOUNDARIES
    """
    user_email = get_email(request.cookies.get("token"))
    prompt = prompt.replace(" I ", f" @{user_email} ")
    if prompt.startswith("I "):
        prompt = "@" + user_email + prompt[1:]
    """

    # TODO: concurrency, an exhibit could have been introduced here

    parsed_prompt, email = parse_prompt(prompt)
    cur.execute("INSERT INTO exhibit(prompt) VALUES (?) RETURNING exhibit_id", (prompt,))
    exhibit_id = cur.fetchone()[0]
    db.commit()

    token = get_token(email)

    # TODO URGENT: JWT could be invalid or expired
    while True:
        # we probably want to specify n_samples and seed in case the user wants
        # more results but for the moment w/e
        print("REQUESTING")
        response = requests.post(VANA_GENERATION_URL_SYNC, 
            headers={
                "authorization": f"Bearer {token}"
            },
            json={
                "prompt": parsed_prompt,
            })
        
        json_response = response.json()
        if not ("success" in json_response and json_response["success"]) and json_response["statusCode"] == 500 and json_response["message"] == "Unable to run Text to Image. Please try again.":
            continue

        assert response.ok, (response, json_response)

        urls = list(map(lambda url: url["url"], json_response["data"]))
        # TODO this may never execute but the exhibit was already inserted causing integrity issues
        cur.executemany("INSERT INTO image(imageUrl, ExhibitId) VALUES (?, ?)", zip(urls, itertools.repeat(exhibit_id)))
        db.commit()

        return jsonify(urls)

@bp.post("/post")
def create_post():
    # necessary otherwise request.data may be empty
    assert request.content_type == "text/markdown"

    token = request.cookies.get("token")
    assert token != None
    
    email = get_email(token)

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO post(PostContent, PosterEmail) VALUES (?, ?)", (request.data, email))
    db.commit()

    # possible return a redirection in case we're dealing with a light client
    return Response(status=204)

@bp.route("/images")
def get_images():
    db = get_db()
    cur = db.cursor()

    prompt = request.args.get("prompt")
    assert prompt != None
    # TODO: well we probably want to restrict to only people who can make images
    # of that kind

    # TODO: this 404 is not necessary
    cur.execute("SELECT exhibit_id FROM exhibit WHERE prompt = ?", (prompt,))
    id = cur.fetchone()
    if not id:
        return Response(status=404)
    id = id[0]
    assert type(id) == int

    _, email = parse_prompt(prompt)
    token = get_token(email)
    exihibit = requests.get(vana_exhibit_url_for_id(id), headers={
        "authorization": f"Bearer {token}",
    }).json()

    # Even when the exhibit doesn't exist this assertion should pass
    # This is a BUG(?) with vana's API
    assert exihibit["success"], exihibit

    if len(exihibit["urls"]) == 0:
        return jsonify({"success": False})

    return jsonify(exihibit)
    
@bp.get("/users")
def get_users():
    """
    returns the list of users with email starting with startsWith query
    parameter or all users, this is to be used for email address completion
    inside of the editor
    """

    startsWith = request.args.get("startsWith", "")
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT email FROM user WHERE instr(email, ?) == 1", (startsWith,))
    return jsonify(list(map(lambda x: x[0], cur.fetchall())))

@bp.post("/posts")
def save_post():
    token = request.cookies.get("token")
    assert token != None

    content = request.json.get("content")
    if content == None:
        return Response(status=400)

    email = get_email(token)

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO post(PostContent, PosterEmail) VALUES (?, ?)", (content, email))
    db.commit()

    return Response(status=200)

@bp.post("/follow/<string:email>")
def follow(email):
    token = request.cookies.get("token")

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO follow(follower, followee) VALUES (?, ?)", (get_email(token), email))
    db.commit()

    return Response(status=204)

@bp.post("/unfollow/<string:email>")
def unfollow(email):
    token = request.cookies.get("token")
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM follow WHERE follower = ? AND followee = ?", (get_email(token), email))
    db.commit()

    return Response(status=204)
