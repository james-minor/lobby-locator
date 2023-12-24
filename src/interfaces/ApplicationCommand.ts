import { CommandInteraction, SlashCommandBuilder } from 'discord.js';

/**
 * The ApplicationCommand interface represents a Discord application command.
 */
export default interface ApplicationCommand
{
	data: SlashCommandBuilder,								// The data for the application command. Name, description, etc.
	execute: (interaction: CommandInteraction) => void,		// The function that executes when the command is invoked.
}