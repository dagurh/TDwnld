import requests
import pandas as pd
from datetime import datetime, timezone
import webbrowser
import math
import re


def convert_size(bytes):
    bytes = int(bytes)
    if bytes > 1*10**9:
        num = bytes/(1024**3)
        return f"{round(num,2)} GB"
    else:
        num = bytes*0.00000095367432
        return f"{round(num,2)} MB"


response_json = None

def getIMDBID(search, key):
    try:
        response = requests.get(
            "http://www.omdbapi.com",
            headers={"Accept": "application/json"},
            params={"t": search, "apikey": key}
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Handle API-specific errors (e.g., movie not found, invalid API key)
        if "imdbID" in data:
            return data["imdbID"]
        elif "Error" in data:
            raise ValueError(f"OMDB API Error: Serie/{data['Error']}. Check spelling")
        else:
            raise ValueError("Unexpected API response structure")
    
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as ve:
        print(f"Data error: {ve}")
        return None    


def getTorrents(selected_page, imdb):
    try:
        response = requests.get(
            "https://EZTVx.to/api/get-torrents",
            headers={"Accept": "application/json"},
            params={"page": selected_page, "limit": 100, "imdb_id": imdb}
        )

        response.raise_for_status()

        data = response.json()

        if data["torrents_count"] != 0:
            totalTorrents = data["torrents_count"]
            totalPages = math.ceil(totalTorrents / 100)
            print(f"Total torrents found: {totalTorrents}")

            if (totalPages > 1):
                i = 2
                while i <= totalPages:
                    responseAdditional_json = requests.get("https://EZTVx.to/api/get-torrents",
                                        headers={"Accept": "application/json"},
                                        params={"page": i, 
                                                "limit": 100, 
                                                "imdb_id": imdb}).json()
                    data["torrents"] = data["torrents"] + responseAdditional_json["torrents"]
                    i += 1
            return data
        
        elif "Error" in data:
            raise ValueError(f"EZTV API Error: {data['Error']}.")
        
        else:
            print("No torrents found")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as ve:
        print(f"Data error: {ve}")
        return None 
        

while response_json == None:

    search = input("What show should I check? ")
    selected_page = 1

    with open("API_key.txt") as file:
        key = file.read()

    imdb_full = getIMDBID(search, key)

    if imdb_full != None:
        imdb = imdb_full[2:]
        print(f"IMDB-ID: {imdb}")

        response_json = getTorrents(selected_page, imdb)


size = len(response_json["torrents"])

titles = []
seasons = []
episodes = []
dates = []
magnets = []
sizes = []

numbers = [i for i in range(1, size+1)]

for item in response_json["torrents"]:
    titles.append(item["title"])
    seasons.append(int(item["season"]))
    episodes.append(int(item["episode"]))
    dates.append(datetime.fromtimestamp(
        item["date_released_unix"], timezone.utc).strftime('%H:%M  %d/%m/%Y'))
    sizes.append(convert_size(item["size_bytes"]))
    magnets.append(item["magnet_url"])

d = {"Number": numbers, 'Titles': titles[0:size], 'Season': seasons[0:size],
     'Episode': episodes[0:size], 'Sizes': sizes[0:size], "Dates": dates[0:size], 'Links': magnets[0:size]}

df = pd.DataFrame(data=d)
df.set_index("Number")

def get_latest():

    max_season = df["Season"].max()
    max_season_df = df[df["Season"] == max_season]

    max_episode = max_season_df["Episode"].max()

    latest_episodes_df = max_season_df[max_season_df["Episode"] == max_episode]

    latest_episodes_df = latest_episodes_df.reset_index(drop=True)

    noOfRows = len(latest_episodes_df)

    for i in range(noOfRows):
        print(f"{i}: Size={latest_episodes_df.iloc[i,4]}MB, Title:  {latest_episodes_df.iloc[i,1]}")
        
    index = 0

    while True:
        try:
            index = int(input("select file to download (index number)"))
            if 0 <= index < noOfRows:
                break
            else:
                print(f"File does not exist, enter a number between 0 and {noOfRows - 1}.")
        except ValueError:
            print("Invalid input. please enter a number")

    webbrowser.open(latest_episodes_df.iloc[index, 6])


def get_ep_seas(y, x):

    s = y
    e = x

    chosen_season_df = df[df["Season"] == s]
    chosen_episode_df = chosen_season_df[chosen_season_df["Episode"] == e]
    chosen_episode_df = chosen_episode_df.reset_index(drop=True)

    noOfRows = len(chosen_episode_df)

    if (noOfRows != 0):

        for i in range(noOfRows):
            print(f"{i}: Size={chosen_episode_df.iloc[i,4]}MB, Title:  {chosen_episode_df.iloc[i,1]}")
        
        index = 0

        while True:
            try:
                index = int(input("select file to download (index number): "))
                if 0 <= index < noOfRows:
                    break
                else:
                    print(f"File does not exist, enter a number between 0 and {noOfRows - 1}. ")
            except ValueError:
                print("Invalid input. please enter a number or CTRL+C to exit ")

        webbrowser.open(chosen_episode_df.iloc[index, 6])
    
    else:
        print("Unable to find requested episode")
        return

def listAll():
    print("Available Episodes")
    df_cleaned = df.drop_duplicates(subset=["Season","Episode"], keep="first")
    df_final = df_cleaned[["Season","Episode"]].copy()
    df_final.sort_values(by=["Season", "Episode"], ascending=[False, False], inplace=True)
    print(df_final)

def download():
    user_input = ""

    while "stop" not in user_input:
        user_input = input("(S,E), latest, list or stop: ")

        try:
            if "latest" in user_input.lower():
                get_latest()
            elif "list" in user_input.lower():
                listAll()
            elif re.match(r"^(?:[1-9]\d?|99),(?:[1-9]\d?|99)$", user_input):
                season, episode = user_input.split(",")
                get_ep_seas(int(season), int(episode))
            elif "stop" in user_input.lower():
                return
            else:
                print("INCORRECT FORMAT\nLastest: See latest episodes\nList: List all available episodes\nSeason,Episode: List certain episode fx. 1,15")
        except:
            print("An unexpected error has occured")


download()
