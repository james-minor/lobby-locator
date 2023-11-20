package com.james_minor.gameseeker;

import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

/**
 * The Steam class handles connecting to the Steam API, and managing the returned SteamApp data.
 */
public class Steam
{
	/**
	 * The connection URL for the Steam database.
	 */
	private static final String steamDatabaseURL = "jdbc:sqlite::memory:";

	/**
	 * The URL to the public Steam API, used to fetch all Steam Apps.
	 */
	private static final String steamAppURL = "https://api.steampowered.com/ISteamApps/GetAppList/v0002";

	/**
	 * The Connection to the SteamApp database.
	 */
	private Connection connection;

	/**
	 * Default constructor for the Steam class.
	 */
	public Steam()
	{
		/* Initializing the database.
		 */
		createDatabaseConnection();
		createDatabaseTables();

		/* Fetching and populating the Steam Apps.
		 */
		long startTime = System.nanoTime();

		JSONArray fetchedApps = fetchSteamApps();
		populateSteamAppsTable(fetchedApps);

		long endTime = System.nanoTime();
		long executionTime = (endTime - startTime) / 1_000_000;  // The execution time (ms) of populating the database.

		System.out.printf("Added %d Steam Apps in %d milliseconds.%n", fetchedApps.length(), executionTime);
	}

	/**
	 * Creates the SQLConnection for the Steam database.
	 */
	private void createDatabaseConnection()
	{
		try
		{
			this.connection = DriverManager.getConnection(steamDatabaseURL);
		} catch (SQLException e)
		{
			throw new RuntimeException(e);
		}
	}

	/**
	 * Creates all the database tables for the Steam database.
	 */
	private void createDatabaseTables()
	{
		try
		{
			this.connection.prepareStatement(
					"CREATE TABLE IF NOT EXISTS steam_apps (id INT PRIMARY KEY, name VARCHAR(255))"
			).executeUpdate();
		} catch (SQLException e)
		{
			throw new RuntimeException(e);
		}
	}

	/**
	 * Fetches the SteamApps from the Steam API.
	 *
	 * @return JSONArray of every application on Steam.
	 */
	private JSONArray fetchSteamApps()
	{
		/* Initializing the HTTP client for the Steam API.
		 */
		HttpClient client = HttpClient.newHttpClient();
		HttpRequest request = HttpRequest.newBuilder()
				.uri(URI.create(steamAppURL))
				.GET()
				.build();

		/* Attempting to fetch the data from the Steam API.
		 */
		try
		{
			HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
			if (response.statusCode() != 200)
			{
				throw new RuntimeException("Steam API may be down, or updated endpoint. Could not connect to Steam.");
			}

			JSONObject json = new JSONObject(response.body());
			return new JSONArray(json.getJSONObject("applist").getJSONArray("apps"));
		} catch (Exception e)
		{
			throw new RuntimeException("Error opening the HttpClient.");
		}
	}

	/**
	 * Populates the Steam Apps database table with a passed JSONArray of SteamApp values.
	 *
	 * @param steamApps A JSONArray of SteamApp objects.
	 */
	private void populateSteamAppsTable(JSONArray steamApps)
	{
		/* Attempting to fetch all listed Steam applications from the Steam API.
		 */
		try
		{
			for (int i = 0; i < steamApps.length(); i++)
			{
				JSONObject app = steamApps.getJSONObject(i);
				if (app.getString("name").length() > 0)
				{
					addSteamApp(app.getInt("appid"), app.getString("name"));
				}
			}
		} catch (Exception e)
		{
			e.printStackTrace();
		}
	}

	/**
	 * Adds a Steam Application to the in-memory SteamApp database.
	 *
	 * @param id   The Steam AppID of the SteamApp.
	 * @param name The name of the SteamApp.
	 */
	private void addSteamApp(int id, String name)
	{
		try (PreparedStatement statement = this.connection.prepareStatement(
				"INSERT OR REPLACE INTO steam_apps (id, name) VALUES (?, ?)"
		))
		{
			statement.setInt(1, id);
			statement.setString(2, name);
			statement.executeUpdate();
		} catch (SQLException e)
		{
			throw new RuntimeException(e);
		}
	}
}
