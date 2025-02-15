import requests


# Retrieve IMDB ID to use for torrent search
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
        
        # Handle API-specific errors (e.g., serie/movie not found, invalid API key)
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


# Retrieve all TV show torrents with selected title
def getTVShowTorrents(imdb):
    try:
        response = requests.get(
            "https://EZTVx.to/api/get-torrents",
            headers={"Accept": "application/json"},
            params={"page": 1, "limit": 100, "imdb_id": imdb}
        )

        # Check if the request was successful
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Handle API-specific errors (e.g., serie not found, invalid API key)
        if data["torrents_count"] != 0:
            totalTorrents = data["torrents_count"]
            totalPages = math.ceil(totalTorrents / 100)
            print(f"Total torrents found: {totalTorrents}")

            # If the response has over 100 torrents we iterate 
            # through pages to retrieve all available torrents
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


def getMovieTorrents(imdb):
    try:
        response = requests.get("https://yts.mx/api/v2/movie_details.json?",
            headers={"Accept": "application/json"},
            params={"imdb_id": imdb
                    }
        )

        response.raise_for_status()

        data = response.json()

        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as ve:
        print(f"Data error: {ve}")
        return None
