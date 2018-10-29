from functools import wraps

from flask import abort
from flask import request
from flask import current_app
from twilio.request_validator import RequestValidator

# Copied from
# https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests
def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create an instance of the RequestValidator class.
        validator = RequestValidator(current_app.config['TWILIO_AUTH_TOKEN'])

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
