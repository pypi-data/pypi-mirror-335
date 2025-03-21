# SteamUser API Wrapper

A Python class to interact with the Steam Web API, providing access to user information, friends lists, game libraries, achievements, and recently played games.

## Features

- **Fetch Friends List**: Retrieve the Steam user's friends, with an option to return only Steam IDs.
- **User Summary**: Access high-level profile information like name, avatar, and online status.
- **Owned Games**: Retrieve the list of games owned by the user, including playtime details.
- **User Game Stats**: Get game-specific statistics and achievement progress for a given game.
- **Recently Played Games**: Fetch the user's recently played games along with playtime information.

## Installation

Ensure you have Python 3.8+ installed and the `requests` package:

```bash
pip install requests
```

## Usage

1. Import the `SteamUser` class.
2. Instantiate the class with your Steam API key and the target Steam ID.

```python
from steam_user import SteamUser

# Initialize the SteamUser object
user = SteamUser(api_key="YOUR_API_KEY", steam_id="76561198012345678")
```

### Methods

#### `getFriendsList()`

Fetches the user's friends list.

- **Returns:**
  - `list`: List of friends with details.

- **Example:**

```python
friends = user.getFriendsList()
print(friends)
```

#### `getUserSummary()`

Retrieves a summary of the user's profile.

- **Returns:**
  - `dict`: Profile information including Steam ID, name, avatar, and more.

- **Example:**

```python
summary = user.getUserSummary()
print(summary)
```

#### `getOwnedGames()`

Fetches the list of games owned by the user.

- **Returns:**
  - `dict`: Game details including app ID, name, and playtime.

- **Example:**

```python
games = user.getOwnedGames()
print(games)
```

#### `getUserGameStats(APP_ID)`

Fetches stats and achievements for a specific game.

- **Parameters:**
  - `APP_ID` (int): The Steam application ID of the game.

- **Returns:**
  - `dict`: Game-specific stats and achievements.

- **Example:**

```python
stats = user.getUserGameStats(105600)  # Terraria
print(stats)
```

#### `getRecentlyPlayed()`

Retrieves the user's recently played games.

- **Returns:**
  - `dict`: Details of recently played games and playtime information.

- **Example:**

```python
recent_games = user.getRecentlyPlayed()
print(recent_games)
```

## Notes

- The Steam API is subject to privacy settings. If data is restricted, methods may return `None` or incomplete information.
- Ensure your API key is valid and the Steam ID is correct.

## License

This project is licensed under the MIT License.

