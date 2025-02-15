from datetime import datetime, timezone
import pandas as pd

# Converts size to a more readable format
def convert_size(bytes):
    bytes = int(bytes)
    if bytes > 1*10**9:
        num = bytes/(1024**3)
        return f"{round(num,2)} GB"
    else:
        num = bytes*0.00000095367432
        return f"{round(num,2)} MB"

def populateDataFrame(response_json, type):

    match type:
        case "tvshow":
            size = len(response_json["torrents"])

            titles = []
            seasons = []
            episodes = []
            dates = []
            magnets = []
            sizes = []

            numbers = [i for i in range(1, size+1)]

            # Populate the arrays from response_json
            for item in response_json["torrents"]:
                titles.append(item["title"])
                seasons.append(int(item["season"]))
                episodes.append(int(item["episode"]))
                dates.append(datetime.fromtimestamp(
                    item["date_released_unix"], timezone.utc).strftime('%H:%M  %d/%m/%Y'))
                sizes.append(convert_size(item["size_bytes"]))
                magnets.append(item["magnet_url"])

            d = {"Number": numbers,
                'Titles': titles[0:size],
                'Season': seasons[0:size],
                'Episode': episodes[0:size],
                'Sizes': sizes[0:size],
                "Dates": dates[0:size],
                'Links': magnets[0:size]}

            df = pd.DataFrame(data=d)
            df.set_index("Number")
            df.title = "tvshow"
        
        case "movie":
            movieInfo = response_json["data"]["movie"]
            size = len(movieInfo["torrents"])

            hash = []
            quality = []
            video_codec = []
            seeds = []
            sizes = []

            numbers = [i for i in range(1, size+1)]

            for item in movieInfo["torrents"]:
                hash.append(item["hash"])
                quality.append(item["quality"])
                video_codec.append(item["video_codec"])
                seeds.append(item["seeds"])
                sizes.append(item["size"])
            
            d = {"Number": numbers,
                'Hash': hash[0:size],
                'Quality': quality[0:size],
                'Video_Codec': video_codec[0:size],
                'Seeds': seeds[0:size],
                'Size': sizes[0:size]}

            df = pd.DataFrame(data=d)
            df.set_index("Number")
            df.title = "movie"
            df.movie_name = movieInfo["title"]
    
    return df