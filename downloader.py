import requests
import pandas as pd
from datetime import datetime
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


search = input("What show should I check? ")
selected_page = 1

with open("API_key.txt") as file:
    key = file.read()

imdb_full = requests.get("http://www.omdbapi.com",
                         headers={"Accept": "application/json"},
                         params={"t": search, 
                                 "apikey": key}).json()["imdbID"]

imdb = imdb_full[2:]
print(imdb)

response_json = requests.get("https://EZTVx.to/api/get-torrents",
                             headers={"Accept": "application/json"},
                             params={"page": selected_page, 
                                     "limit": 100, 
                                     "imdb_id": imdb}).json()

totalTorrents = response_json["torrents_count"]
totalPages = math.ceil(totalTorrents / 100)
print(f"Total torrents: {totalTorrents}, Total pages: {totalPages}")

if (totalPages > 1):
    i = 2
    while i <= totalPages:
        responseAdditional_json = requests.get("https://EZTVx.to/api/get-torrents",
                             headers={"Accept": "application/json"},
                             params={"page": i, 
                                     "limit": 100, 
                                     "imdb_id": imdb}).json()
        response_json["torrents"] = response_json["torrents"] + responseAdditional_json["torrents"]
        i += 1

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
    seasons.append(item["season"])
    episodes.append(item["episode"])
    dates.append(datetime.utcfromtimestamp(
        item["date_released_unix"]).strftime('%H:%M  %d/%m/%Y'))
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

    s = str(y)
    e = str(x)

    chosen_season_df = df[df["Season"] == s]
    chosen_episode_df = chosen_season_df[chosen_season_df["Episode"] == e]
    chosen_episode_df = chosen_episode_df.reset_index(drop=True)

    noOfRows = len(chosen_episode_df)

    for i in range(noOfRows):
        print(f"{i}: Size={chosen_episode_df.iloc[i,4]}MB, Title:  {chosen_episode_df.iloc[i,1]}")
        
    index = 0

    while True:
        try:
            index = int(input("select file to download (index number): "))
            if 0 <= index < noOfRows:
                break
            else:
                print(f"File does not exist, enter a number between 0 and {noOfRows - 1}.")
        except ValueError:
            print("Invalid input. please enter a number: ")

    webbrowser.open(chosen_episode_df.iloc[index, 6])

def listAll():
    print("Available Episodes")
    df_filtered = df[["Season","Episode"]]
    print(df_filtered)
    df_cleaned = df.drop_duplicates(subset=["Season","Episode"], keep="first")
    df_final = df_cleaned[["Season","Episode"]]
    df_final.sort_values(by=["Season", "Episode"], ascending=[False, False], inplace=True)
    print(df_final)

def download():
    user_input = ""

    while "stop" not in user_input:
        user_input = input("(s,e), latest, list or stop: ")

        try:

            # new or latest for latest episode

            if "latest" in user_input:
                get_latest()
            elif "list" in user_input:
                listAll()
            elif re.match(r"^[1-99]\d+,[1-99]\d+$", user_input):
                season, episode = user_input.split(",")
                get_ep_seas(int(season), int(episode))
            else:
                print("Please input in correct format\nLastest: See latest episodes\nList: List all available episodes\nSeason,Episode: List certain episode fx. 1,15")
        except:
            print("An unexpected error has occured")


download()
