# --------------------------- local dev ----------------------------
.PHONY: run
run: .bootstrapped
	FLASK_ENV=development OAUTHLIB_INSECURE_TRANSPORT=1 FLASK_APP=gatekeeper.server pipenv run flask run

.bootstrapped: Pipfile Pipfile.lock
	pipenv install
	touch .bootstrapped

.PHONY: lint
lint:
	pylint gatekeeper

# --------------------------- deployment ---------------------------
.PHONY: deploy
deploy: docker
	docker login
	docker push jfly/gatekeeper
	scp docker/traefik.toml moria:/tmp/traefik.toml
	rsync -azP --delete instance moria:/tmp/gatekeeper-instance
	# TODO - potentially move this to systemd? see https://coreos.com/os/docs/latest/getting-started-with-systemd.html
	ssh moria "\
		set -e; \
		docker pull jfly/gatekeeper; \
		docker stop gatekeeper && docker rm gatekeeper || true; \
		docker run -d --name gatekeeper -p 5000:5000 --volume /tmp/gatekeeper-instance:/app/instance --label=traefik.frontend.rule=Host:moria.jflei.com jfly/gatekeeper:latest; \
		docker stop traefik && docker rm traefik || true; \
		touch /tmp/acme.json && chmod 600 /tmp/acme.json && docker run -d --name traefik --volume /var/run/docker.sock:/var/run/docker.sock --volume /tmp/traefik.toml:/traefik.toml --volume /tmp/acme.json:/acme.json -p 8080:8080 -p 80:80 -p 443:443 traefik; \
	"

.PHONY: docker
docker:
	docker build --pull=true . -t jfly/gatekeeper
