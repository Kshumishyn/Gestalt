const Discord = require("discord.js");
const lineReader = require('line-reader');
const fs = require('fs');
const client = new Discord.Client();
//const translate = require('translate');
const async = require('async');
const util = require('util');

// Sets Geralto version
let version = "15";

// Set the prefix
let prefix = "!";

// Builds Command Map
let commandList = new Map();

// Builds Time multiplier
let timeMap = new Map([
	['millisecond', 1],
	['msec', 1],
	['milliseconds', 1],
	['msecs', 1],
	['second', 1000],
	['sec', 1000],
	['seconds', 1000],
	['secs', 1000],
	['minute', 60000],
	['min', 60000],
	['minutes', 60000],
	['mins', 60000],
	['hour', 3600000],
	['hr', 3600000],
	['hours', 3600000],
	['hrs', 3600000],
	['day', 86400000],
	['days', 86400000],
	['week', 604800000],
	['weeks', 604800000]
]);

// Builds list of valid countries
let countryList = [
	"az", "sq", "am", "en", "ar", "hy", "af", "eu", "ba",
	"be", "bn", "my", "bg", "bs", "cy", "hu", "vl", "ht",
	"gl", "nl", "mrj", "el", "ka", "gu", "da", "he", "yi",
	"id", "ga", "it", "is", "es", "kk", "kn", "ca", "ky",
	"zh", "ko", "xh", "km", "lo", "la", "lv", "lt", "lb",
	"mg", "ms", "ml", "mt", "mk", "mi", "mr", "mhr", "mn",
	"de", "ne", "no", "pa", "pap", "fa", "pl", "pt", "ro",
	"ru", "ceb", "sr", "si", "sk", "sl", "sw", "su", "tg",
	"th", "ti", "ta", "tt", "te", "tr", "udm", "uz", "uk",
	"ur", "fi", "fr", "hi", "hr", "cs", "sv", "gd", "et", 
	"eo", "jv", "ja"
];

// String of List
let comList = "Dynamic Commands:```";

// Max
const MAX_COMM = 15;
const MAX_TRIM = 100;

// Fetches the authorization code
let authCode = fs.readFileSync('discordAuth.code', 'utf8').trim();

// Fetches the yandex api key
//let yandCode = fs.readFileSync('yand.code', 'utf8').trim();

// Bot starts
client.on("ready", client => {
	console.log("Geralto V" + version + "! Now with " + version + "x more DAKKA!");

	// Reads in command file, line by line
	lineReader.eachLine("commands.grlt", function(line, last) {
		
	// Builds Map
	let cmd = line.substr(0,line.indexOf(' '));
	let str = line.substr(line.indexOf(' ')+1);
	   	commandList.set(cmd, str);
	
	// Builds String of List
	let offset = "";
	for (let i = cmd.length; i < MAX_COMM; i++)
		offset += " ";

		// Trims the display mappings
        if (str.length > MAX_TRIM)
            str = str.substring(0, MAX_TRIM) + "...";


	// Creates display message for comList
	comList += "\t!" + cmd + offset + "=> " + str + "\n";

	// Detects when last line has been reached and stops reading
	if (last) {
		comList += "```";
		return false;
	}
	});
});

// Bot detects message
client.on("message", async (message) => {
    // Exit and stop if the prefix is not there or if user is a bot
    if (!(message.content.startsWith(prefix)) || message.author.bot)
		return;

	let command = (message.content).substr(1);
	let mesUser = message.member.user.username.toString();
	let mesUsr2 = message.member.user.id;
	let mesDate = (new Date()).toLocaleString();

	// Handles simple "!" call
	if (command.length == 0)
		message.channel.send("Write something after the ! stoopid!").catch(error => logError(error));

	// Handles a request to log off bot
    else if (command.startsWith("begone"))
        begoneCommand();

    // Handles help command
    else if (command.startsWith("help"))
        message.channel.send(helpCommand()).catch(error => logError(error));

	// Handles comList commands
	else if (command.startsWith("comlist"))
		message.channel.send(comListCommand(command)).catch(error => logError(error));

	// Handles translate command
	/*else if (command.startsWith("translate"))
		message.channel.send(await translateCommand(command)).catch(error => logError(error));

	// Translate To shortcut
	else if (command.startsWith("ttj"))
		message.channel.send(await quickTranslateTo(command)).catch(error => logError(error));

	// Translate From shortcut
	else if (command.startsWith("tfj"))
		message.channel.send(await quickTranslateFrom(command)).catch(error => logError(error));
	*/
	// Handles dice roll
	else if (command.startsWith("rolld") && !(isNaN(command.substr(5))) && (command.indexOf(" ") == -1))
		message.channel.send(diceCommand(command, mesUser)).catch(error => logError(error));

	// Dice Roll shortcut
	else if (command.startsWith("d") && !(isNaN(command.substr(1))) && (command.indexOf(" ") == -1))
		message.channel.send(diceCommand("roll" + command, mesUser)).catch(error => logError(error));

	// Multi Dice Roll
	else if (command.startsWith("rolld") && (command.indexOf(" ") >= 0))
		message.channel.send(diceMultiCommand(command.substring(0, command.indexOf(" ")), mesUser, command.substring(command.indexOf(" ")))).catch(error => logError(error));

	// Multi Dice Roll shortcut
	else if (command.startsWith("d") && (command.indexOf(" ") >= 0))
        message.channel.send(diceMultiCommand("roll" + command.substring(0, command.indexOf(" ")), mesUser, command.substring(command.indexOf(" ")))).catch(error => logError(error));

	// Handles Remind command
	else if (command.startsWith("remind"))
		message.channel.send(await remindCommand(command.substring(command.indexOf(" ") + 1), mesUsr2)).catch(error => logError(error));

	// Checks if dynamic command exists
	else if (commandList.has(command))
		message.channel.send(commandList.get(command)).catch(error => logError(error));

	// Handles no matching commands
	else
		message.channel.send("Unknown command!").catch(error => logError(error));

	// Appends command to file for future use
	let stream = fs.createWriteStream("messages.log", {flags:'a'});
	stream.write(mesDate + " - " + mesUser + ": " + command  + "\n");
	stream.end();

	// After any command is entered, delete it
	message.delete();

});

client.on('error', err => {logError(util.inspect(err));});

// Log Error
function logError(error) {
	let date = (new Date()).toLocaleString();
	let stream = fs.createWriteStream("error.log", {flags:'a'});
    stream.write("\n" + date + "\n" + error + "\n");
	stream.end();
}

// Form !help
function helpCommand(display) {
	let helpStr	 = "Here is a list of all logistic commands:```";
	helpStr		+= "    !help           : You're currently using this command\n";
	helpStr		+= "    !begone         : Logs this bot off (warning, must restart locally)\n";
	helpStr		+= "    !comlist view   : Lists out the dynamic commands from configuration\n";
	helpStr		+= "    !comlist add    : Sets dynamic command x to make bot say y\n";
	helpStr		+= "    !comlist remove : Removes dynamic command x from configuration\n";
	/*helpStr		+= "    !translate to   : Translates from English to a specified language\n";
	helpStr		+= "    !translate from : Translates to English from a specified language\n";
	helpStr		+= "    !ttj            : Translates English to Japanese\n";
	helpStr		+= "    !tfj            : Translates to English from Japanese\n";*/
	helpStr		+= "    !rolldx         : Rolls a dice with values from 2->x\n";
	helpStr		+= "    !dx             : Shortcut to roll dice from 2->x\n";
	helpStr		+= "    !rolldx y       : Rolls y dx's\n";
	helpStr		+= "    !dx y           : Rolls y dx's\n";
	helpStr		+= "	!remind x y z	: Reminds x (username or \"me\") for y amount of time in unit x\n";

	helpStr		+= "    * Ask Kosba if you need another question answered, help commands are a PITA\n";
	helpStr		+= "```";

	return helpStr;
}

// Form !rolld[integer]
function diceCommand(command, user) {
	let message = user + " just tried to roll a less than 2 sided die!";
	let number = parseInt(command.substr(5), 10);
	
	// Exits prematurely if invalid roll
	if (number < 2)
		return message;

	let roll = Math.round(Math.random()*(number - 1)) + 1;

	if (roll === number)
		message = "*" + user + " rolled a " + number + " sided die and got **a natural " + number + "!***";
	else
		message = "*" + user + " rolled a " + number +  " sided die:*   〚⊱" + roll + "⊰〛";
	
	return message;
}

// Form !rolld[integer] [integer]
function diceMultiCommand(command, user, num) {
	let message = user + ", Multi-dice Roll failed!";

	if (isNaN(num))
		return message;

	let number = parseInt(num, 10);
	message = user + " rolled " + number + " dice and got the following:\n\n";

	for (let i = 0; i < number; i++)
		message = message + diceCommand(command, user) + "\n";

	return message;
}

// Form !comList [option] [string] [?string]
function comListCommand(command) {
	let message = "";
	let option = command.substr(8);

	if (option.toLowerCase().startsWith("view"))
		return comList;
	else if (option.toLowerCase().startsWith("add"))
		message = comListAdd(option.substr(4));
	else if (option.toLowerCase().startsWith("remove"))
		message = comListRemove(option.substr(7));
	else
		message = "Unknown comlist command";

	return message;
}

// Form [string] [string]
function comListAdd(keyAndValue) {
	let key = keyAndValue.substring(0, keyAndValue.indexOf(' '));
	let value = keyAndValue.substring( keyAndValue.indexOf(' ') + 1);

	if (commandList.has(key))
		return "Command already exists, try removing existing command first.";
	
	if (keyAndValue.length == 0 || key.length == 0 || value.length == 0)
		return "Invalid command mapping length";

	commandList.set(key, value);

	let offset = "";
    for (let i = key.length; i < MAX_COMM; i++)
        offset += " ";

	let trimValue = value;
	if (trimValue.length > MAX_TRIM)
		trimValue = trimValue.substring(0, MAX_TRIM) + "...";
	
	comList = comList.substring(0, comList.length - 3);
    comList += "\t!" + key + offset + "=> " + trimValue + "\n```";

	// Appends command to file for future use
	let stream = fs.createWriteStream("commands.grlt", {flags:"a"});
    stream.write(keyAndValue + "\n");
    stream.end();

	// Gives Mapping Feedback
	// TODO: Make conditional
	return "Mapped \"" + key + "\" to \"" + value + "\"."
}

// Form [string]
function comListRemove(key) {
	if (!commandList.has(key))
		return "Command does not exist.";
	
	let value = commandList.get(key);
	let command = key + " " + value + "\n";
	let trimValue = value;

	commandList.delete(key);

	let offset = "";
    for (let i = key.length; i < MAX_COMM; i++)
		offset += " ";

    if (trimValue.length > MAX_TRIM)
        trimValue = trimValue.substring(0, MAX_TRIM) + "...";

	// Erases from comList
    trimValue = "\t!" + key + offset + "=> " + trimValue + "\n";
    comList = comList.replace(trimValue, "");

	// Replaces removed Dynamic Messages in configuration file
    fs.readFile("commands.grlt", "utf8", function (err,data) {
        if (err)
            return console.log(err);

        let result = data.replace(command, "");

        fs.writeFile("commands.grlt", result, "utf8", function (err) {
            if (err) return console.log(err);
		});
    });

	// Gives Removal Feedback
	// TODO: Make conditional
	return "Removed \"!" + key + "\" from mapping.";
}

// Form !translate [option] [code] [string]
/*function translateCommand(command) {
    let str = command.substr(10);
	let option = str.substring(0, str.indexOf(" "));
	str = str.substring(option.length).trim();

	let code = str.substring(0, str.indexOf(" "));
	let text = str.substring(str.indexOf(" ") + 1);

    if (!countryList.includes(code))
		return "Country Code does not exist.";
	
	if (option.startsWith("to"))
		return translate(text, { to: code, engine: "yandex", key: yandCode });


	else if (option.startsWith("from"))
		return translate(text, { from: code, engine: "yandex", key: yandCode });

	else
		return "Option \"to\" or \"from\" is malformed.";
}

// Shortcut translate to
// Form !ttj [string]
function quickTranslateTo(command) {
	let text = command.substring(command.indexOf(" ") + 1);

	return translate(text, { to: "ja", engine: "yandex", key: yandCode });
}

// Shortcut translate from
// Form !tfj [string]
function quickTranslateFrom(command) {
	let text = command.substring(command.indexOf(" ") + 1);

	return translate(text, { from: "ja", engine: "yandex", key: yandCode });
}*/

// Returns a message but only after a specific delay 
function delayMessage(delay, message, user) {
	return new Promise(resolve => {
		setTimeout(() => {
			let result = "<@" + user + "> " + message;
			resolve(result);
		}, delay);
	});
}

// Form !remind [target] [number] [unit]
async function remindCommand(command, mesUser) {
	let args = command.split(" ");

	// Just !remind or !remind [target]
	if (args.length < 2)
		return "Insufficient Arguments.\n\tFormat: !remind [target] [number] [unit]";

	let target = args[0];
	if (target == "me")
		target = mesUser;
	else
	{
		try {
			target = client.users.find(user => user.username === target).id;	
		} catch (e) {
			return "Invalid Username provided. Lookup failed.";
		}
	}

	let num = parseInt(args[1], 10);
	if (isNaN(num))
		return "Expected Argument Number couldn't be parsed.\n\tFormat: !remind [target] [number] [unit]";
	
	let unit = args[2];
	if (!timeMap.has(unit))
		return "Invalid unit provided, if you think it belongs, message me and I'll add it!";

	let mult = timeMap.get(unit);
	let delay = num * mult;

	let ret = "";
	if (args.length > 3)
		for (let i = 3; i < args.length; i++)
			ret += (args[i] + " ");

	return delayMessage(delay, ret, target);
}

// Form !begone
function begoneCommand() {
	process.exit();
}

// Authentication token
client.login(authCode);
