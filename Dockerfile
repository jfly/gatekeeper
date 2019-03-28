FROM python:alpine3.7

RUN pip install pipenv

WORKDIR /app

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy

COPY gatekeeper ./gatekeeper

EXPOSE 5000
ENTRYPOINT ["/usr/local/bin/waitress-serve", "--port=5000", "--url-scheme=https", "--call", "gatekeeper:server.create_app"]
