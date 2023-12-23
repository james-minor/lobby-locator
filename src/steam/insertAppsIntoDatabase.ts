import { Game } from '@prisma/client';
import prismaClient from '../prismaClient.ts';
import SteamApp from './SteamApp.ts';

/**
 * Inserts a passed SteamApp array into the local database.
 * @param apps The SteamApp objects to insert into the database.
 */
export default async function insertAppsIntoDatabase(apps: SteamApp[])
{
	// If the supplied apps array is empty, we will use our existing data instead of attempting to update the data.
	if (apps.length == 0)
	{
		return;
	}
	
	// Converting the passed SteamApps array to a Game model array. Allowing us to leverage the createMany function.
	const gameData: Game[] = apps.map(({appid, name}): Game =>
		({
			steamId: appid,
			name,
		}));
	
	// Inserting the converted SteamApp data into the database.
	prismaClient.game.createMany({
		data: gameData,
		skipDuplicates: true,
	})
		.then((result) =>
		{
			console.log(`Successfully inserted ${ result.count } new app(s) into the database!`);
		})
		.catch(e =>
		{
			console.warn('Could not insert apps into the database.');
			console.warn(e);
		});
	
}