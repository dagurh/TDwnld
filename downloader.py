import webbrowser
import re
from APIhandler import getIMDBID, getMovieTorrents, getTVShowTorrents
from dataHandler import populateDataFrame

# Initialize response_json
response_json = None
df = None

# While response_json is empty we keep asking for serie/movie title
while response_json == None:

    movieOrShow = input("Movie or Show? (M/S): ")
    titleSearch = input("Search Title: ")

    with open("API_key.txt") as file:
        key = file.read()


    imdb_full = getIMDBID(titleSearch, key)

    imdb = None

    if imdb_full != None:
        imdb = imdb_full[2:]
        print(f"IMDB-ID: {imdb}")

    if movieOrShow.lower() == "m":
        response_json = getMovieTorrents(imdb)
        df = populateDataFrame(response_json, "movie")
    elif movieOrShow.lower() == "s":
        response_json = getTVShowTorrents(imdb)
        df = populateDataFrame(response_json, "tvshow")
    else:
        print("Input error: select 'm' for Movie and 's' for TV show")

def get_latest():

    # Create a new dataframe with latest season, episode listed
    max_season = df["Season"].max()
    max_season_df = df[df["Season"] == max_season]

    max_episode = max_season_df["Episode"].max()

    latest_episodes_df = max_season_df[max_season_df["Episode"] == max_episode]

    latest_episodes_df = latest_episodes_df.reset_index(drop=True)

    noOfRows = len(latest_episodes_df)

    # Lists all available torrents of the latest episode
    for i in range(noOfRows):
        print(f"{i}: Size={latest_episodes_df.iloc[i,4]}MB, Title:  {latest_episodes_df.iloc[i,1]}")
        
    index = 0

    # Index selection of listed torrents
    while True:
        try:
            index = int(input("select file to download (index number)"))
            if 0 <= index < noOfRows:
                break
            else:
                print(f"File does not exist, enter a number between 0 and {noOfRows - 1}.")
        except ValueError:
            print("Invalid input. please enter a number")

    # Opens magnet link from chosen episode
    webbrowser.open(latest_episodes_df.iloc[index, 6])


def get_ep_seas(y, x):

    s = y
    e = x

    # Create a new dataframe from selected season, episode
    chosen_season_df = df[df["Season"] == s]
    chosen_episode_df = chosen_season_df[chosen_season_df["Episode"] == e]
    chosen_episode_df = chosen_episode_df.reset_index(drop=True)

    noOfRows = len(chosen_episode_df)

    # if the dataframe is empty, no torrents with that episode was found
    if (noOfRows != 0):

        for i in range(noOfRows):
            print(f"{i}: Size={chosen_episode_df.iloc[i,4]}MB, Title:  {chosen_episode_df.iloc[i,1]}")
        
        index = 0

        # Index selection of listed torrents
        while True:
            try:
                index = int(input("select file to download (index number): "))
                if 0 <= index < noOfRows:
                    break
                else:
                    print(f"File does not exist, enter a number between 0 and {noOfRows - 1}. ")
            except ValueError:
                print("Invalid input. please enter a number or CTRL+C to exit ")

        # Opens magnet link from chosen episode
        webbrowser.open(chosen_episode_df.iloc[index, 6])
    
    else:
        print("Unable to find requested episode")
        return

# Lists all episodes found
def listAll():
    print("Available Episodes")
    # Remove duplicate season, episode listings from the dataframe
    df_cleaned = df.drop_duplicates(subset=["Season","Episode"], keep="first")
    df_final = df_cleaned[["Season","Episode"]].copy()
    df_final.sort_values(by=["Season", "Episode"], ascending=[False, False], inplace=True)
    print(df_final)

def getMovies():

    print(df.movie_name)
    for row in df.itertuples(index=True):
        print(f"Index: {row.Index}, Size: {row.Size}, Quality: {row.Quality}, Seeds: {row.Seeds}")

    index = int(input("Select torrent to download by index number: "))

    magnet = generateMagnetLink(df.iloc[index,1], df.iloc[index,2])

    webbrowser.open(magnet)


def generateMagnetLink(hash, quality):

    trackers = [
        "udp://glotorrents.pw:6969/announce",
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://torrent.gresille.org:80/announce",
        "udp://tracker.openbittorrent.com:80",
        "udp://tracker.coppersurfer.tk:6969",
        "udp://tracker.leechers-paradise.org:6969",
        "udp://p4p.arenabg.ch:1337",
        "udp://tracker.internetwarriors.net:1337"
    ]

    trackerString = "&tr=" + "&tr=".join(trackers)

    return f"magnet:?xt=urn:btih:{hash}&dn={df.movie_name}+{quality}&tr=http://track.one:1234/announce&tr=udp://track.two:80{trackerString}"


def download():
    
    if df.title == "movie":
        getMovies()

# Calls methods based on user input
def downloadTVShow():
    user_input = ""

    while "stop" not in user_input:
        user_input = input("(S,E), latest, list or stop: ")

        try:
            if "latest" in user_input.lower():
                get_latest()
            elif "list" in user_input.lower():
                listAll()
            # Check if input is in the format [1:99],[1:99]
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
