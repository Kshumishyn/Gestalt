const Discord = require("discord.js");
const lineReader = require('line-reader');
const fs = require('fs');
const client = new Discord.Client();
//const translate = require('translate');

// Sets Geralto version
var version = "6";

// Set the prefix
var prefix = "!";

// Builds Map
var commandList = new Map();

// String of List
var comList = "Dynamic Commands:```";

// Max
const MAX_COMM = 15;
const MAX_TRIM = 100;

// Bot starts
client.on("ready", client => {
	console.log("Geralto V" + version + "!");

	// Reads in command file, line by line
	lineReader.eachLine("commands.grlt", function(line, last) {
		
		// Builds Map
		let cmd = line.substr(0,line.indexOf(' '));
		let str = line.substr(line.indexOf(' ')+1);
	    commandList.set(cmd, str);
	
		// Builds String of List
		let offset = "";
		for (var i = cmd.length; i < MAX_COMM; i++)
			offset += " ";

		// Trims the display mappings
        if (str.length > MAX_TRIM) {
            str = str.substring(0, MAX_TRIM) + "...";
        }

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
client.on("message", (message) => {
    // Exit and stop if the prefix is not there or if user is a bot
    if (!(message.content.startsWith(prefix)) || message.author.bot)
		return;

	// If message starts with a prefix
    if (message.content.startsWith(prefix)) {
		let command = (message.content).substr(1);
	
		let mesUser = message.member.user.username.toString();
	
		// Handles simple "!" call
		if (command.length == 0) {
			message.channel.send("Write something after the ! stoopid!");
			return;
		}
		
		// Handles adding new commands dynamically
		if (command.startsWith("#")) {
			// Stores command into current list
			command = command.substr(1);
			let temp = command.substring(0,command.indexOf(' '));
			command = command.substring(command.indexOf(' ')+1);
	
			// Existing command
			if (commandList.has(temp)) {
				message.channel.send("Already exists, try removing first");
				return;
			}
			// Empty command
			if (temp.length == 0 || command.length == 0) {
				message.channel.send("Empty Command addition");
				return;
			}

			// Successfully Maps command
			commandList.set(temp, command);

			// Updates comList
            let offset = "";
            for (var i = temp.length; i < MAX_COMM; i++)
                offset += " ";

			// Trims the display mappings
            let trimmed = command;
            if (trimmed.length > MAX_TRIM) {
                trimmed = trimmed.substring(0, MAX_TRIM) + "...";
            }

			// Appends to end of comList
			comList = comList.substring(0, comList.length - 3);
            comList += "\t!" + temp + offset + "=> " + trimmed + "\n```";
			
			// Feedback
			message.channel.send("Mapped \"" + temp + "\" to \"" + trimmed + "\".");

			// Reuse to append to file
			temp = temp + " " + command;
			
			// Appends command to file for future use
			let stream = fs.createWriteStream("commands.grlt", {flags:'a'});
			stream.write(temp + "\n");
			stream.end();
		}

        // Handles removing commands from dynamic command list
		else if (command.startsWith("$")) {
			command = command.substr(1);

			// If command does not exist in the map, it's time to stop
			if (!commandList.has(command)) {
				message.channel.send("Command does not exist");
				return;
			}

			// Stores for two uses
			let tempa = commandList.get(command);
			let tempb = commandList.get(command);
			tempa = command + " " + tempa + "\n";

			// Feedback
            message.channel.send("Removed \"!" + command + "\" from mapping.");

			// Deletes instances of corresponding command
			commandList.delete(command);

			// Updates comList
			let offset = "";
			for (var i = command.length; i < MAX_COMM; i++)
				offset += " ";

			// Trims the display mapping
            if (tempb.length > MAX_TRIM) {
                tempb = tempb.substring(0, MAX_TRIM) + "...";
            }

			// Erases from comList
			tempb = "\t!" + command + offset + "=> " + tempb + "\n";
			comList = comList.replace(tempb, "");

            // Replaces removed Dynamic Messages in configuration file
			fs.readFile("commands.grlt", 'utf8', function (err,data) {
				if (err)
					return console.log(err);
				
				var result = data.replace(tempa, "");

				fs.writeFile("commands.grlt", result, 'utf8', function (err) {
					if (err) return console.log(err);
				});
			});

		}

        // Handles a request to log off bot
        else if (command.startsWith("begone")) {
			process.exit();
		}

        // Handles help command
		else if (command.startsWith("help")) {
			message.channel.send(helpCommand());
		}

        // Handles printing list of current artificial commands
		else if (command.startsWith("comlist"))
			message.channel.send(comList);

		// Checks if dynamic command exists
		else if (commandList.has(command))
			message.channel.send(commandList.get(command));

		// Assumes
		else if (command.startsWith("d") && !(isNaN(command.substr(1)))) {
			command = command.substr(1);
			let num = parseInt(command,10);
			let rand = Math.round(Math.random()*(num-1))+1;
			let mes = "";
			if (rand == num)
				//mes = "*" + mesUser + " rolled a " + num + " sided die and got **a natural " + num + "!***";
				mes = "Winnar is " + mesUser + ".";
			//else if (rand == 1)
			//	mes = "*" + mesUser + " rolled a " + num + " sided die and got a 1, **critical fail!***";
			else
				mes = "*" + mesUser + " rolled a " + num +  " sided die:*   〚⊱" + rand + "⊰〛";

			message.channel.send(mes);
		}

		/*else if (command.startsWith("&")) {
			let mes = command.substr(1);
			let str = "";

			for (var i = 0; i < mes.length; i++) {
				let temp = parseInt(mes.charCodeAt(i));
				str = str + " " + temp;
			}
			message.channel.send(str);
		}*/

		// Handles no matching commands
		else
			message.channel.send("Unknown command!");
		
		// After any command is entered, delete it
		message.delete();
    }
});

function helpCommand() {
	var helpStr	 = "Here is a list of all logistic commands:```";
	helpStr		+= "	!help    : You're currently using this command\n";
	helpStr		+= "	!begone  : Logs this bot off (warning, must restart locally)\n";
	helpStr		+= "	!comlist : Lists out the dynamic commands from configuration\n";
	helpStr		+= "	!#x y    : Sets dynamic command x to make bot say y\n";
	helpStr		+= "	!$x      : Removes dynamic command x from configuration\n";
	helpStr		+= "	!dx      : Rolls a dice with values from 1->x\n";

	helpStr		+= "```";
	return helpStr;
}

// Authentication token
client.login("NTAyNzMyNTcxOTczNzc5NDY2.Dq8Obw.fjQDWGuvW67WPVzJzQsehe9jd-Y");
