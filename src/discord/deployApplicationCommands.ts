import { Collection, REST, Routes } from 'discord.js';
import ApplicationCommand from '../interfaces/ApplicationCommand.ts';

/**
 * Deploys a collection of Application Commands to Discord. This will refresh the command globally on Discord's servers.
 */
export default async function deployApplicationCommands(commands: Collection<string, ApplicationCommand>)
{
	// Initializing the REST connection to the Discord API.
	const rest = new REST().setToken(String(process.env.DISCORD_BOT_TOKEN));
	
	// Iterating over the command collection and placing the data into an array (to push to Discord API).
	const commandData: any[] = [];
	commands.forEach((value, key) =>
	{
		commandData.push(value.data.toJSON())
	});
	
	// Attempting to push commands to Discord.
	try
	{
		console.log('Starting application command refresh...');
		
		await rest.put(
			Routes.applicationCommands(String(process.env.DISCORD_APPLICATION_ID)),
			{ body: commandData },
		);
		
		console.log(`Successfully refreshed application commands!`);
	}
	catch (e)
	{
		console.warn(e);
	}
}