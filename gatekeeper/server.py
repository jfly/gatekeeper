import logging

from werkzeug.contrib.fixers import ProxyFix
from requestlogger import WSGILogger, ApacheFormatter
from flask import Flask

from . import auth
from . import routes

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('gatekeeper.cfg')
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

    auth.setup(app)
    routes.add_routes(app)

    return app
