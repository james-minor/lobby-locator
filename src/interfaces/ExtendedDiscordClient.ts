import { Client, Collection } from 'discord.js';
import ApplicationCommand from './ApplicationCommand.ts';

/**
 * The ExtendedDiscordClient interface allows us to extend the existing Discord client class and add custom properties.
 * Useful to allow for easily storing information we want to be globally accessible with the Discord client.
 */
export default interface ExtendedDiscordClient extends Client
{
	applicationCommands: Collection<string, ApplicationCommand>,
	applicationCooldowns: any,
}
