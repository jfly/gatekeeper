var https = require('https');
var fs = require('fs');

var express = require('express');
var nconf = require('nconf');
var xmlbuilder = require('xmlbuilder');

nconf.argv().env().file({ file: "config.json" });
nconf.defaults({
	port: 8000,
	passphrase: null
});
var port = nconf.get("port");

var options = {
	key: fs.readFileSync('server.key'),
	cert: fs.readFileSync('server.crt'),
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
	return req.protocol + "://" + req.get('host') + ( file || "" );
}

function generateGandalfXml(req) {
	var response = xmlbuilder.create("Response");

	var gather = response.ele("Gather", { numDigits: "5", action: getUrl(req, "/password-entered.xml"), method: "GET" });
	gather.ele("Play", null, getUrl(req, "/media/speakfriendandenter.mp3"));
	return response;
}

app.get("/gatekeeper.xml", function(req, res) {
	console.log("Call started: " + JSON.stringify(req.query));
	
	var response = generateGandalfXml(req);
	response.children[0].insertBefore("Play", { digits: '1' })
		.com("Accept google voice call");

	res.header("Content-Type", "text/xml");
	var responseStr = response.end({ pretty: true });
	res.end(responseStr);
});

app.get("/password-entered.xml", function(req, res) {
	var digits = req.query.Digits;

	var response;
	if(digits == "12345") {
		response = xmlbuilder.create("Response");
		response.ele("Say", null, "Correct password");
		response.ele("Play", { digits: '9' });
	} else {
		response = generateGandalfXml(req);
		response.children[0].insertBefore("Play", null, getUrl(req, "/media/shallnotpass.wav"));
	}

	res.header("Content-Type", "text/xml");
	var responseStr = response.end({ pretty: true });
	res.end(responseStr);
});

app.get("/gatekeeper-callend.xml", function(req, res) {
	console.log("Call ended");
});
