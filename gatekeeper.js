var fs = require('fs');

var express = require('express');
var nconf = require('nconf');
var xmlbuilder = require('xmlbuilder');

nconf.argv().env().file({ file: "config.json" });
nconf.defaults({
    port: 8000,
});
var port = nconf.get("port");

var options = {}

var app = express();
app.enable('trust proxy');//<<<

var server = app.listen(port, function() {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Listening at http://%s:%s', host, port);
});

app.use("/media", express.static(__dirname + "/media"));

function getUrl(req, file) {
    console.log(req.headers['x-forwarded-proto']);//<<<
    console.log(JSON.stringify(req.headers));//<<<
    console.log(req.protocol + "://" + req.get('host') + ( "/" + file || "" ));//<<<
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

function generateCallForwardXml(req, phoneNumber) {
    var response = xmlbuilder.create("Response");

    var dial = response.ele("Dial", {}, phoneNumber);
    return response;
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
    //var response = generateCallForwardXml(req, "949-981-9345"); // jfly cell
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
    } else if(digits == "54321") {
        response = xmlbuilder.create("Response");
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

app.get("/gatekeeper-sms.xml", function(req, res) {
    console.log("Incoming SMS" + JSON.stringify(req.query));
    res.header("Content-Type", "text/plain");
    res.end("Thanks for the message!")
});
