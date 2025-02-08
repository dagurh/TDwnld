from re import S
from xml.etree.ElementTree import tostring
import requests
import pandas as pd
from datetime import datetime
import webbrowser


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

    print(latest_episodes_df.iloc[index, 1])
    webbrowser.open(latest_episodes_df.iloc[index, 6])


def get_ep_seas(y, x):

    s = str(y)
    e = str(x)

    chosen_season_df = df[df["Season"] == s]
    print(chosen_season_df)
    chosen_episode_df = chosen_season_df[chosen_season_df["Episode"] == e]
    chosen_episode_df = chosen_episode_df.reset_index(drop=True)

    noOfRows = len(chosen_episode_df)

    for i in range(noOfRows):
        print(f"{i}: Size={chosen_episode_df.iloc[i,4]}MB, Title:  {chosen_episode_df.iloc[i,1]}")
        
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

    print(chosen_episode_df.iloc[index, 1])
    webbrowser.open(chosen_episode_df.iloc[index, 6])


def download():
    x = ""
    y = ""

    while "stop" not in x or "stop" not in y:
        y = input("Which Season? ")
        x = input("Which Episode should I download? ")

        try:

            # new or latest for latest episode

            if "new" in x or "latest" in x:
                get_latest()
            elif "new" in x or "latest" in y:
                get_latest()
            else:
                get_ep_seas(int(y), int(x))
        except:
            print("An error has occured")


download()