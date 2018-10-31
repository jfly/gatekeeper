import os
import random
import logging

from flask import request
from flask import url_for
from flask import redirect
from flask import render_template
from flask_dance.contrib.google import google
from twilio.twiml.voice_response import Gather
from twilio.twiml.voice_response import VoiceResponse

import dataclasses
from .util import validate_twilio_request

logger = logging.getLogger(__name__)

texts = []

def add_routes(app):
    @app.route("/")
    def index():
        if not google.authorized:
            return redirect(url_for("google.login"))
        resp = google.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        user = User.from_google_userinfo(resp.json())
        return render_template(
            'index.html',
            user=user,
            texts=texts,
        )

    @app.route("/gatekeeper.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def gatekeeper():
        logger.info("Call started: %s", request.values)

        response = VoiceResponse()

        if 'notFirstCall' not in request.values:
            # Accept Google voice call
            response.play(digits='1')

        add_gandalf_to_response(response)

        return str(response)

    @app.route("/password-entered.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def password_entered():
        digits = request.values['Digits']
        logger.info("Password entered: %s", digits)

        response = VoiceResponse()
        if digits == "12345":
            correct_clip = pick_random_file("correct")
            response.play(correct_clip)
            response.play(digits="9")
        elif digits == "54321":
            response.play(digits="99")
        else:
            wrong_clip = pick_random_file("wrong")
            response.play(wrong_clip)
            add_gandalf_to_response(response)

        return str(response)

    @app.route("/gatekeeper-callend.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def callend():
        logger.info("Call ended")
        return 'Bye!'

    @app.route("/gatekeeper-sms.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def sms():
        logger.info("Incoming SMS %s", request.values)

        texts.append(Text(
            from_number=request.values['From'],
            body=request.values['Body'],
        ))

        return "Thanks for the message!"

    def add_gandalf_to_response(response):
        gather = Gather(num_digits=5, action=url_for('.password_entered'))
        challenge_clip = pick_random_file("challenge")
        gather.play(challenge_clip)
        response.append(gather)
        response.redirect(url_for(".gatekeeper", notFirstCall='true'))

    def pick_random_file(folder):
        abs_folder = os.path.join(app.static_folder, folder)
        file = random.choice(os.listdir(abs_folder))
        return f"/static/{folder}/{file}"

@dataclasses.dataclass
class Text:
    from_number: str
    body: str

@dataclasses.dataclass
class User:
    email: str
    short_name: str

    @classmethod
    def from_google_userinfo(cls, userinfo):
        return cls(
            short_name=userinfo['given_name'],
            email=userinfo['email'],
        )

    def trusted(self):
        return self.email in ['jeremyfleischman@gmail.com']
