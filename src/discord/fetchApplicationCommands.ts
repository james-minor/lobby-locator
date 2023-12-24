import path from 'node:path';
import * as fs from 'node:fs';
import { fileURLToPath } from 'url';
import ExtendedDiscordClient from '../interfaces/ExtendedDiscordClient.ts';

/**
 * Fetches the Discord Application Commands and places them into the passed ExtendedDiscordClient's command collection.
 */
export default async function fetchApplicationCommands(discordClient: ExtendedDiscordClient)
{
	// The current directory of this file. Analogous to the __dirname constant used in commonjs.
	const currentDirectory = path.dirname(fileURLToPath(new URL(import.meta.url)));
	
	// The directory path of the command directory. This is where the Application Command files are stored.
	const commandsDirectoryPath = path.join(currentDirectory, 'commands');
	
	try
	{
		// Iterating over the command directory files.
		const commandsDirectory = fs.readdirSync(commandsDirectoryPath);
		for (const commandFile of commandsDirectory)
		{
			// The imported command file.
			const command = await import('file://' + path.join(commandsDirectoryPath, commandFile));

			// Filtering only valid command files.
			if (commandFile.endsWith('.ts') && 'data' in command && 'execute' in command)
			{
				discordClient.applicationCommands.set(command.data.name, command);
			}
			else
			{
				console.warn(`Malformed command file: ${commandFile}`);
			}
		}
	} catch (e)
	{
		console.warn(e);
	}
}