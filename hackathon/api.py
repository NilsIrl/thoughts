from flask import Blueprint, jsonify, request, Response
import requests
import re
from hackathon.db import get_db

bp=Blueprint("api", __name__, url_prefix="/api")

VANA_LOGIN_URL = "https://api.vana.com/api/v0/auth/login"
VANA_GENERATION_URL = "https://api.vana.com/api/v0/jobs/text-to-image"
VANA_GET_EXHIBIT_URL = "https://api.vana.com/api/v0/account/exhibits"

def vana_exhibit_url_for_id(id: int) -> str:
    return f"{VANA_GET_EXHIBIT_URL}/thoughts_{id}"

EMAIL_PATTERN = re.compile(r"@(\w+@\w+.\w+)")

# Abstract class (TM)
class InvalidPromptError(Exception):
    pass

class NoEmailInvalidPromptError(InvalidPromptError):
    pass

class MultipleEmailInvalidPromptError(InvalidPromptError):
    pass

def get_token(email: str) -> str:
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT token FROM user WHERE email = ?", (email,))
    return cur.fetchone()

def get_email(token: str) -> str:
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT email FROM user WHERE token = ?", (token,))
    return cur.fetchone()

def email_exists(email):
    print(email)
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM user WHERE email = ?", (email,))
    count = cur.fetchone()[0]

    return count > 1

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
        raise InvalidPromptError() from exc
    
    final_prompt = prompt[:first_email.start(0)] + "{target_token}"
    end_of_previous = first_email.end(0) + 1

    for email_match in email_matches:
        if email_match.group(1) != first_email:
            raise MultipleEmailInvalidPromptError()
        final_prompt += prompt[end_of_previous:email_match.start(0)] + "{target_token}"
        end_of_previous = email_match.end(0) + 1

    final_prompt += prompt[end_of_previous:]

    return final_prompt, first_email

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

@bp.route("/user_exists")
def user_exists():
    user_email = request.args.get("email")
    return jsonify(email_exists(user_email))


@bp.route("/images", methods = ["POST"])
def generate_images():
    db = get_db()
    cur = db.cursor()
    prompt = request.args.get("prompt")
    assert prompt != None
    authorization_header = request.headers.get("authorization")
    
    cur.execute("SELECT COUNT(*) FROM exhibit WHERE prompt = ?", (prompt,))
    if cur.fetchone()[0] > 0:
        # Prompt already exists
        pass
    
    parsed_prompt, email = parse_prompt(prompt)
    cur.execute("INSERT INTO exhibit(prompt) VALUES (?) RETURNING exhibit_id", (prompt,))
    exhibit_id = cur.fetchone()

    # this should probably be a tuple
    print(exhibit_id)
    assert type(exhibit_id) == str

    db.commit()

    token = get_token(email)
    # TODO URGENT: JWT could be invalid or expired
    response = requests.post(VANA_GENERATION_URL, 
        headers={
            "authorization": f"Bearer {token}"
        },
    json={
        "prompt": parsed_prompt,
        "exhibit_name": f"thoughts_{exhibit_id}",
        # we probably want to specify n_samples and seed in case the user wants
        # more results but for the moment w/e
    });
    assert response.ok, response

    return Response(status=204)


@bp.post("/post")
def create_post():
    token = request.cookies.get("token")
    email = get_email(token)
    assert type(email) == str, email

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO post(PostContent, PostEmail) VALUES (?, ?)", (request.data, email))
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

    cur.execute("SELECT exhibit_id FROM exihibit WHERE prompt = ?", (prompt,))
    id = cur.fetchone()[0]
    assert type(id) == int

    _, email = parse_prompt(prompt)
    token = get_token(email)
    exihibit = requests.get(vana_exhibit_url_for_id(id), headers={
        "authorization": f"Bearer {token}",
    }).json()

    assert exihibit["success"], exihibit

    if len(exihibit["urls"]) == 0:
        return jsonify({"success": False})

    return jsonify(exihibit)
    
