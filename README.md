gatekeeper
==========

I ain't 'fraid of no ghost.


- openssl genrsa -des3 -out server.key 1024
- openssl req -new -key server.key -out server.csr
- openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
- `npm install`
- `node gatekeeper.js`

- You can create a file called config.json to control the behavior of the server.
