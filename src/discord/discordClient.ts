import { Client, Collection, GatewayIntentBits } from 'discord.js';
import ExtendedDiscordClient from '../interfaces/ExtendedDiscordClient.ts';

// Globally accessible Discord client object.
const discordClient = new Client({
	intents: [GatewayIntentBits.Guilds],
}) as ExtendedDiscordClient;

// Initializing client collections.
discordClient.applicationCommands = new Collection();
discordClient.applicationCooldowns = new Collection();

export default discordClient;