package com.james_minor.gameseeker;

public class Main
{
	public static void main(String[] args)
	{
		System.out.println("Attempting connection to Steam API...");
		Steam steam = new Steam("https://api.steampowered.com/ISteamApps/GetAppList/v0002");
	}
}