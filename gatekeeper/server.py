import logging
from functools import wraps

import oauthlib
from werkzeug.contrib.fixers import ProxyFix
from requestlogger import WSGILogger, ApacheFormatter
from twilio.request_validator import RequestValidator
from flask_dance.contrib.google import make_google_blueprint, google
from flask import abort, current_app, Flask, redirect, request, url_for, render_template

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('gatekeeper.cfg')
blueprint = make_google_blueprint(
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)
app.register_blueprint(blueprint, url_prefix="/login")
app.wsgi_app = ProxyFix(app.wsgi_app)

### Begin logging configuration
# This feels unecessarily complicated...
# I guess flask run internally uses werkzeug, which does its own request
# logging in additionto the request logging we set up here. To have consisency
# between production and development, we disable werkzeug request logging here,
# and leave all the logging to WSGILogger.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.WARNING)
app.wsgi_app = WSGILogger(app.wsgi_app, [], ApacheFormatter())
### End logging configuration

# Copied from
# https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests
def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create an instance of the RequestValidator class.
        validator = RequestValidator(app.config['TWILIO_AUTH_TOKEN'])

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header.
        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''),
        )

        # Continue processing the request if it's valid (or if DEBUG is True)
        # and return a 403 error if it's not.
        if request_valid or current_app.debug:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function

@app.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    user = resp.json()
    return render_template('index.html', user=user)

# Copied (and modified) from
# https://github.com/spotify/gimme/blob/master/gimme/views.py#L52-L94
# I think this shouldn't be necessary. See
# https://github.com/singingwolfboy/flask-dance/issues/143#issuecomment-416781772
# for more information.
@app.errorhandler(oauthlib.oauth2.rfc6749.errors.TokenExpiredError)
def token_expired(_):
    del app.blueprints['google'].token
    return redirect(url_for('.index'))

@app.route("/test1")
def test1():
    return url_for('.index')

@app.route("/test2")
def test2():
    return url_for('.index', _external=True)

@app.route("/gatekeeper.xml")
@validate_twilio_request
def gatekeeper():
    from twilio.twiml.voice_response import VoiceResponse #<<<

    resp = VoiceResponse()

    # <Say> a message to the caller
    from_number = "HIYA" #request.values['From']
    body = """
    Thanks for calling!

    Your phone number is {0}. I got your call because of Twilio's webhook.

    Goodbye!""".format(' '.join(from_number))
    resp.say(body)

    # Return the TwiML
    return str(resp)

def get_app():
    return app
