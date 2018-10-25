# gatekeeper

I ain't 'fraid of no ghost.

See
<https://docs.google.com/document/d/1VBOR1V1JM4kIiX0m81HyGlqWPDovprEIQ6vNr4nhyOo/#heading=h.8r2bijgjqicz>
for some more information (including Twilio).

## Development

Copy the sample config file and edit it to fill in the missing values.

```
$ cp instance/gatekeeper.cfg.sample instance/gatekeeper.cfg
```

```
$ make run
```

## Deploying

First, update your `~/.ssh/config` so `ssh moria` will take you to a machine with
Docker set up.

```
$ make deploy
```
