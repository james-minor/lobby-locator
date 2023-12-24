import 'dotenv/config';
import fetchAppDataFromSteam from './steam/fetchAppDataFromSteam.ts';
import insertAppsIntoDatabase from './steam/insertAppsIntoDatabase.ts';
import { Events, GatewayIntentBits } from 'discord.js';
import fetchApplicationCommands from './discord/fetchApplicationCommands.ts';
import deployApplicationCommands from './discord/deployApplicationCommands.ts';
import discordClient from './discord/discordClient.ts';

// Fetching data from the Steam API.
const steamApps = await fetchAppDataFromSteam();
console.log(`Fetched ${ steamApps.length } apps from the Steam API...`);

// Inserting Steam data into the database.
await insertAppsIntoDatabase(steamApps);

// Fetching and deploying the Discord application commands into the Discord client.
await fetchApplicationCommands(discordClient);
await deployApplicationCommands(discordClient.applicationCommands);

// Handling the bot startup.
discordClient.once(Events.ClientReady, readyClient =>
{
	console.log(`Logged in as ${ readyClient.user.username }!`);
});

// Handling user interactions with the bot.
discordClient.on(Events.InteractionCreate, async interaction =>
{
	if (!interaction.isChatInputCommand())
	{
		return;
	}
	
	const command = discordClient.applicationCommands.get(interaction.commandName);
	
	if (!command)
	{
		console.warn(`No command matching ${ interaction.commandName } was found.`);
		return;
	}
	
	try
	{
		await command.execute(interaction);
	} catch (e)
	{
		console.error(e);
		
		if (interaction.replied || interaction.deferred)
		{
			await interaction.followUp({
				content: 'There was an internal error while executing this command.',
				ephemeral: true,
			});
		}
		else
		{
			await interaction.reply({
				content: 'There was an internal error while executing this command.',
				ephemeral: true,
			});
		}
	}
});

// Logging in the bot.
await discordClient.login(process.env.DISCORD_BOT_TOKEN);