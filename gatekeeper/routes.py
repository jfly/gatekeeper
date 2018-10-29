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

from .util import validate_twilio_request

logger = logging.getLogger(__name__)

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

    @app.route("/gatekeeper.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def gatekeeper():
        logging.info("Call started: %s", request.values)

        response = VoiceResponse()

        if 'notFirstCall' not in request.values:
            # Accept Google voice call
            response.play(digits='1')

        add_gandalf_to_respose(response)

        return str(response)

    @app.route("/password-entered.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def password_entered():
        digits = request.values['Digits']

        response = VoiceResponse()
        if digits == "12345":
            correct_clip = pick_random_file("correct")
            response.play(correct_clip)
            response.play(digits="9")
        elif digits == "54321":
            response.play(digits='9')
        else:
            wrong_clip = pick_random_file("wrong")
            response.play(wrong_clip)
            add_gandalf_to_respose(response)

        return str(response)

    @app.route("/gatekeeper-callend.xml", methods=['GET', 'POST'])
    @validate_twilio_request
    def callend():
        logging.info("Call ended")
        return 'Bye!'

    def add_gandalf_to_respose(response):
        gather = Gather(num_digits=5, action=url_for('.password_entered'))
        challenge_clip = pick_random_file("challenge")
        gather.play(challenge_clip)
        response.append(gather)
        response.redirect(url_for(".gatekeeper", notFirstCall='true'))

    def pick_random_file(folder):
        abs_folder = os.path.join(app.static_folder, folder)
        file = random.choice(os.listdir(abs_folder))
        return f"/static/{folder}/{file}"
