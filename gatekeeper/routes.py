from flask import url_for
from flask import redirect
from flask import render_template
from flask_dance.contrib.google import google

from .util import validate_twilio_request

def add_routes(app):
    @app.route("/")
    def index():
        if not google.authorized:
            return redirect(url_for("google.login"))
        resp = google.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        user = resp.json()
        return render_template('index.html', user=user)

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
