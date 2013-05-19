var https = require('https');
var fs = require('fs');

var express = require('express');
var nconf = require('nconf');
var xmlbuilder = require('xmlbuilder');

nconf.argv().env().file({ file: "config.json" });
nconf.defaults({
	port: 8000,
	passphrase: null,
	sslkey: 'server.key',
	sslcrt: 'server.crt'
});
var port = nconf.get("port");

var options = {
	key: fs.readFileSync(nconf.get('sslkey')),
	cert: fs.readFileSync(nconf.get('sslcrt')),
	passphrase: nconf.get("passphrase"),
};

var username = nconf.get("username");
var password = nconf.get("password");
if(!username || !password) {
   console.log("Must specify a username and password");
   process.exit(1);
}

var app = express();


https.createServer(options, app).listen(port, function() {
	console.log("Listening on port " + port);
});

var auth = express.basicAuth(
	nconf.get("username"),
	nconf.get("password")
);

app.use(auth);
app.use("/media", express.static(__dirname + "/media"));

function getUrl(req, file) {
	return req.protocol + "://" + req.get('host') + ( "/" + file || "" );
}

function pickRandomFile(folder) {
   var files = fs.readdirSync(folder);
   if(files.length == 0) {
      return null;
   }
   if(folder[folder.length - 1] != '/') {
      folder += '/';
   }
   return folder + files[Math.floor(Math.random()*files.length)];
}

function generateGandalfXml(req) {
	var response = xmlbuilder.create("Response");

	var gather = response.ele("Gather", { numDigits: "5", action: getUrl(req, "password-entered.xml"), method: "GET" });
	var challengeClip = pickRandomFile("media/challenge");
	gather.ele("Play", null, getUrl(req, challengeClip));

	var redirect = response.ele("Redirect", { method: "GET" }, getUrl(req, "gatekeeper.xml?notFirstCall=true"));
	return response;
}

app.get("/gatekeeper.xml", function(req, res) {
	console.log("Call started: " + JSON.stringify(req.query));
	
	var response = generateGandalfXml(req);
	if(!req.query.notFirstCall) {
		response.children[0].insertBefore("Play", { digits: '1' })
			.com("Accept google voice call");
	}

	res.header("Content-Type", "text/xml");
	var responseStr = response.end({ pretty: true });
	res.end(responseStr);
});

app.get("/password-entered.xml", function(req, res) {
	var digits = req.query.Digits;

	var response;
	if(digits == "12345") {
		response = xmlbuilder.create("Response");
                var correctClip = pickRandomFile("media/correct");
                if(correctClip) {
                   response.ele("Play", null, getUrl(req, correctClip));
                } else {
                   response.ele("Say", null, "Correct password");
                }
		response.ele("Play", { digits: '9' });
	} else {
		response = generateGandalfXml(req);
                var wrongClip = pickRandomFile("media/wrong");
		response.children[0].insertBefore("Play", null, getUrl(req, wrongClip));
	}

	res.header("Content-Type", "text/xml");
	var responseStr = response.end({ pretty: true });
	res.end(responseStr);
});

app.get("/gatekeeper-callend.xml", function(req, res) {
	console.log("Call ended");
	res.header("Content-Type", "text/plain");
        res.end("Bye!");
});
