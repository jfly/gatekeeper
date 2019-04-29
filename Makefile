# --------------------------- local dev ----------------------------
.PHONY: run
run: .bootstrapped
	FLASK_ENV=development OAUTHLIB_INSECURE_TRANSPORT=1 FLASK_APP=gatekeeper.server:create_app pipenv run flask run

.bootstrapped: Pipfile Pipfile.lock
	pipenv install --dev
	touch .bootstrapped

.PHONY: lint
lint: .bootstrapped
	pylint gatekeeper

clean:
	rm -f .bootstrapped

# --------------------------- deployment ---------------------------
.PHONY: deploy
deploy: docker
	docker login
	docker push jfly/gatekeeper
	# TODO - find a better directory than /home/jeremyfleischman
	scp docker/traefik.toml moria:/home/jeremyfleischman/traefik.toml
	rsync -azP --delete instance/ moria:/home/jeremyfleischman/gatekeeper-instance/
	ssh moria "\
		set -e; \
		docker pull jfly/gatekeeper; \
		docker stop gatekeeper && docker rm gatekeeper || true; \
		docker run -d --restart unless-stopped --name gatekeeper -p 5000:5000 --volume /home/jeremyfleischman/gatekeeper-instance:/app/instance --label=traefik.frontend.rule=Host:moria.jflei.com jfly/gatekeeper:latest; \
		docker stop traefik && docker rm traefik || true; \
		touch /home/jeremyfleischman/acme.json && chmod 600 /home/jeremyfleischman/acme.json && docker run -d --restart unless-stopped --name traefik --volume /var/run/docker.sock:/var/run/docker.sock --volume /home/jeremyfleischman/traefik.toml:/traefik.toml --volume /home/jeremyfleischman/acme.json:/acme.json -p 8080:8080 -p 80:80 -p 443:443 traefik; \
	"

.PHONY: docker
docker:
	docker build --pull=true . -t jfly/gatekeeper
