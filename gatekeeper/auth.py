import oauthlib

from flask import url_for
from flask import redirect
from flask_dance.contrib.google import make_google_blueprint

def setup(app):
    blueprint = make_google_blueprint(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
    )
    app.register_blueprint(blueprint, url_prefix="/login")

    # Copied (and modified) from
    # https://github.com/spotify/gimme/blob/master/gimme/views.py#L52-L94
    # I think this shouldn't be necessary. See
    # https://github.com/singingwolfboy/flask-dance/issues/143#issuecomment-416781772
    # for more information.
    @app.errorhandler(oauthlib.oauth2.rfc6749.errors.TokenExpiredError)
    def token_expired(_):
        del app.blueprints['google'].token
        return redirect(url_for('.index'))
