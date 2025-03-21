class SteamUser:
    """Initialize a class upon which class methods can be applied to get player information, requires API_KEY and STEAM_ID"""

    def __init__(self, api_key, steam_id):
        self.BASE_URL = "http://api.steampowered.com/"
        self.api_key  = api_key
        self.steam_id = steam_id

    def getFriendsList(self):
        """ Fetches friends list for the steam user.
        
        Returns
        -------
        list of dict
            Returns a list of dictionaries where each dictionary contains:
            - steamid : str
                The unique Steam ID of the friend.
            - relationship : str
                The relationship type (usually 'friend').
            - friend_since : int
                Unix timestamp representing when the friendship was established.

        Examples
        --------
        >>> user = SteamUser(api_key="YOUR_API_KEY", steam_id="76561197960435530")
        >>> user.getFriendsList()
        [{'steamid': '76561197960265731', 'relationship': 'friend', 'friend_since': 0},
        {'steamid': '76561197960265738', 'relationship': 'friend', 'friend_since': 0},...]
        """
        url    = f"{self.BASE_URL}/ISteamUser/GetFriendList/v0001/?key={self.api_key}"
        params = {
            "steamid" : self.steam_id,
            "format"  : "json"
        }
        response = requests.get(url, params = params)
        if response.status_code == 401:
            return None
        
        try:
            data = response.json()
            if "friendslist" not in data:
                return None
        except requests.JSONDecodeError:
            return None

        data = response.json()["friendslist"]["friends"]
        return data

    def getUserSummary(self):
        """
        Fetches a summary of the Steam user's profile information.

        Returns
        -------
        dict
            A dictionary containing information about the Steam user includes, refer to Steam API documentation:
            - Steam ID
            - Profile name and URL
            - Avatar images (small, medium, full)
            - Real name (if available)
            - Account creation time
            - Online status
            - Location information (country, state, city if available)

            Returns None if the request fails.

        Examples
        -------- 
        >>> user = SteamUser(api_key="YOUR_API_KEY", steam_id="76561197960435530")
        >>> user.getUserSummary()
        {'players': [{'steamid': '76561197960435530',
           'communityvisibilitystate': 3,
           'profilestate': 1,
           'personaname': 'Robin',
           'profileurl': 'https://steamcommunity.com/id/robinwalker/',
           'avatar': 'https://avatars.steamstatic.com/81b5478529dce13bf24b55ac42c1af7058aaf7a9.jpg',
           'avatarmedium': 'https://avatars.steamstatic.com/81b5478529dce13bf24b55ac42c1af7058aaf7a9_medium.jpg',
           'avatarfull': 'https://avatars.steamstatic.com/81b5478529dce13bf24b55ac42c1af7058aaf7a9_full.jpg',
           'avatarhash': '81b5478529dce13bf24b55ac42c1af7058aaf7a9',
           'personastate': 0,
           'realname': 'Robin Walker',
           'primaryclanid': '103582791429521412',
           'timecreated': 1063407589,
           'personastateflags': 0,
           'loccountrycode': 'US',
           'locstatecode': 'WA',
           'loccityid': 3961}]}
        
        """
        url = f"{self.BASE_URL}/ISteamUser/GetPlayerSummaries/v0002/?key={self.api_key}"
        params = {
            "steamids" : self.steam_id,
        }
        response = requests.get(url, params = params)
        return response.json()['response']

    def getOwnedGames(self):
        """Fetches the list of games owned by the Steam user.

        Returns
        -------
        dict
            A dictionary containing:
            - game_count : int
                The total number of games owned by the user.
            - games : list of dict
                Each dictionary represents a game and includes:
                - appid : int
                    The unique identifier for the game.
                - name : str
                    The game's name.
                - playtime_forever : int
                    Total playtime in minutes across all platforms.
                - playtime_windows_forever : int
                    Playtime on Windows in minutes.
                - playtime_mac_forever : int
                    Playtime on macOS in minutes.
                - playtime_linux_forever : int
                    Playtime on Linux in minutes.
                - playtime_deck_forever : int
                    Playtime on Steam Deck in minutes.
                - rtime_last_played : int
                    Unix timestamp of the last time the game was played.

            Note
            ----
            - Players' privacy settings may cause this method to return None.
            - If a player's privacy settings hide playtime, all playtime values will be zero.

            Returns None if the request fails.

        Examples
        --------
        >>> user = SteamUser(api_key="YOUR_API_KEY", steam_id="STEAM_ID")
        >>> user.getOwnedGames()
        {'game_count': 73, 'games': [{'appid': 17390, 'name': 'Spore', 'playtime_forever': 250, ...}]}
        """
        url = f"{self.BASE_URL}/IPlayerService/GetOwnedGames/v0001/?key={self.api_key}"
        params = {
            "steamid"                   : self.steam_id,
            "include_appinfo"           : True,
            "include_played_free_games" : True,
            "format"                    : "json"
        }
        response = requests.get(url, params = params)
        return response.json()['response']

    def getRecentlyPlayed(self):
        """
        Fetches the list of games the Steam user has played recently.

        Returns
        -------
        dict
            A dictionary containing:
            - total_count : int
                The total number of recently played games.
            - games : list of dict
                Each dictionary represents a recently played game and includes:
                - appid : int
                    The unique identifier for the game.
                - name : str
                    The game's name.
                - playtime_2weeks : int
                    Playtime in the last two weeks (in minutes).
                - playtime_forever : int
                    Total playtime across all platforms (in minutes).

            Returns None if the request fails or if the user's privacy settings prevent access.

        Examples
        --------
        >>> user = SteamUser(api_key="YOUR_API_KEY", steam_id="STEAM_ID")
        >>> user.getRecentlyPlayed()
        {'total_count': 7, 'games': [{'appid': 629760, 'name': 'MORDHAU', 'playtime_2weeks': 592, 'playtime_forever': 31333,
        ...}]}
        """
        url = f"{self.BASE_URL}/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.api_key}"
        params = {
            "steamid"                   : self.steam_id,
            "format"                    : "json"
        }
        response = requests.get(url, params = params)
        return response.json()['response']

    def getUserGameStats(self, APP_ID):
        """
        Fetches the user's game-specific statistics and achievements for a given game.

        Parameters
        ----------
        APP_ID : int
            The unique identifier of the game for which to retrieve statistics.

        Returns
        -------
        dict
            A dictionary containing:
            - steamID : str
                The Steam ID of the user.
            - gameName : str
                The name of the game.
            - achievements : list of dict
                Each dictionary represents an achievement and includes:
                - name : str
                    The internal name of the achievement.
                - achieved : int
                    Whether the achievement is unlocked (1) or not (0).

            Returns None if the request fails or the user's privacy settings prevent access to game statistics.

        Examples
        --------
        >>> user = SteamUser(api_key="YOUR_API_KEY", steam_id="STEAM_ID")
        >>> user.getUserGameStats(105600)
        {'playerstats': {'steamID': 'STEAM_ID', 'gameName': 'Terraria', 'achievements': [{'name': 'TIMBER', 'achieved':
        1}, ...]}}
        """
        url = f"{self.BASE_URL}/ISteamUserStats/GetUserStatsForGame/v0002/?key={self.api_key}"
        params = {
            "steamid"                   : self.steam_id,
            "appid"                     : APP_ID
        }
        response = requests.get(url, params = params)
        return response.json()