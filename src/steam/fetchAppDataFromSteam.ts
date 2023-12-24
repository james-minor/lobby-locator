import SteamApp from '../interfaces/SteamApp.ts';

/**
 * Fetches the Steam app data for every application on Steam from the Steam API.
 *
 * @return A SteamApp array of every application publicly listed on Steam. If there is an error, returns an empty array.
 */
export default async function fetchAppDataFromSteam(): Promise<SteamApp[]>
{
	try
	{
		// Attempting to fetch the data from the Steam API.
		const response = await fetch('https://api.steampowered.com/ISteamApps/GetAppList/v0002');
		if (!response.ok)
		{
			return [];
		}
		
		// Parsing the response data.
		const blob = await response.blob();
		const data = JSON.parse(await blob.text()).applist.apps;
		
		return data as SteamApp[];
	}
	catch (e)
	{
		return [];
	}
}
