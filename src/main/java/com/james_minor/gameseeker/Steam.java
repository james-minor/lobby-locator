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

public class Steam
{
	private static final String steamDatabaseURL = "jdbc:sqlite::memory:";

	private static final String steamAppURL = "https://api.steampowered.com/ISteamApps/GetAppList/v0002";

	private final Connection connection;

	public Steam()
	{
		/* Initializing the Steam app database tables.
		 */
		try
		{
			this.connection = DriverManager.getConnection(steamDatabaseURL);
			this.connection.prepareStatement(
					"CREATE TABLE IF NOT EXISTS steam_apps (id INT PRIMARY KEY, name VARCHAR(255))"
			).executeUpdate();
		}
		catch (SQLException e)
		{
			throw new RuntimeException(e);
		}

		/* Initializing the HTTP client for the Steam API.
		 */
		HttpClient client = HttpClient.newHttpClient();
		HttpRequest request = HttpRequest.newBuilder()
				.uri(URI.create(steamAppURL))
				.GET()
				.build();

		/* Attempting to fetch all listed Steam applications from the Steam API.
		 */
		try
		{
			long startTime = System.nanoTime();

			HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
			if (response.statusCode() != 200)
			{
				throw new Exception("Could not connect to the steam API.");
			}

			JSONObject json = new JSONObject(response.body());
			JSONArray jsonArray = new JSONArray(json.getJSONObject("applist").getJSONArray("apps"));

			for (int i = 0; i < jsonArray.length(); i++)
			{
				JSONObject app = jsonArray.getJSONObject(i);
				if (app.getString("name").length() > 0)
				{
					addSteamApp(app.getInt("appid"), app.getString("name"));
				}
			}

			long endTime = System.nanoTime();
			long executionTime = (endTime - startTime) / 1_000_000;

			System.out.printf("Added %d Steam Apps in %d milliseconds.%n", jsonArray.length(), executionTime);
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	private void addSteamApp(int id, String name)
	{
		try (PreparedStatement statement = this.connection.prepareStatement(
				"INSERT OR REPLACE INTO steam_apps (id, name) VALUES (?, ?)"
		)) {
			statement.setInt(1, id);
			statement.setString(2, name);
			statement.executeUpdate();
		} catch (SQLException e)
		{
			throw new RuntimeException(e);
		}
	}
}
