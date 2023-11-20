package com.james_minor.gameseeker;

import org.json.JSONArray;
import org.json.JSONObject;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;

public class Steam
{
	private ArrayList<SteamApp> apps = new ArrayList<SteamApp>();

	public Steam(String apiUrl)
	{
		HttpClient client = HttpClient.newHttpClient();
		HttpRequest request = HttpRequest.newBuilder()
				.uri(URI.create(apiUrl))
				.GET()
				.build();

		try
		{
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
				System.out.println(app);

				// TODO: create an SQLite database.
				// TODO: store apps within an SQLite Database.
			}
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}

	public ArrayList<SteamApp> getApps()
	{
		return this.apps;
	}
}
