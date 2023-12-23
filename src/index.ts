import fetchAppDataFromSteam from './steam/fetchAppDataFromSteam.ts';
import insertAppsIntoDatabase from './steam/insertAppsIntoDatabase.ts';

async function main()
{
	// Fetching data from the Steam API.
	const steamApps = await fetchAppDataFromSteam();
	console.log(`Fetched ${steamApps.length} apps from the Steam API...`);
	
	// Inserting Steam data into the database.
	await insertAppsIntoDatabase(steamApps);
}

main();