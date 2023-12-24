/**
 * The SteamApp interface represents the entry of the Steam App in the Valve database. Useful to define contracts for
 * data before they are placed within the application database.
 */
export default interface SteamApp
{
	appid: number,	// The Steam App ID, for example: 730
	name: string,	// The Steam App Name, for example: Counter-Strike 2
}