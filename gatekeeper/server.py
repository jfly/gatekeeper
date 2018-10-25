import oauthlib

from flask import Flask, redirect, url_for, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.contrib.fixers import ProxyFix

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

def get_app():
    return app
