import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import requests
from pytube import YouTube
import urllib.request
import re
from datetime import datetime

folder_name = "Spotify Downloads"

download_location = os.path.join(os.getcwd(), folder_name)
if not os.path.exists(download_location):
    os.mkdir(folder_name)
    print("There Was No Folder Present in the name. Automatically Created...")

# !------------------------------SPOTYIFY AUTH-------------------------
load_dotenv(dotenv_path='.env')
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URL")
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-library-read playlist-read-private playlist-read-collaborative",
)
token_info = sp_oauth.get_cached_token()
if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(f"Please go to this URL and authorize the app: {auth_url}")
    auth_code = input("Enter the authorization code: ")
    token_info = sp_oauth.get_access_token(auth_code)
access_token = token_info["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# !-------------------------------------------------GET PLAYLIST TRACK------------------------------------
def getPlaylist(token, playlist_id):
    tracks = []
    global playlist_name
    headers = get_auth_header(token)
    response = requests.get(
        "https://api.spotify.com/v1/playlists/"+playlist_id, headers=headers)
    response_json = response.json()
    playlist_name = response_json["name"]
    for item in response_json["tracks"]["items"]:
        tracks.append(
            {
                'id' : item["track"]["id"],
                'name' : item["track"]["name"],
                'artists' : [j["name"] for j in item["track"]["artists"]]
            }
        )
    return tracks


def getSong(token, track_id):
    headers = get_auth_header(token)
    response = requests.get(
        "https://api.spotify.com/v1/tracks/"+track_id, headers=headers)
    response_json = response.json()
    name = response_json["name"]
    artists = []
    for i in response_json["artists"]:
        artists.append(i["name"])
    return f"{name}-{''.join(i for i in artists)}"


# !--------------------------------DOWNLOAD SONGS-------------------------------
def downloadSong(tracks, folder_name):
    global download_location
    download_location = os.path.join(download_location, folder_name)

    for track in tracks:
        try:
            search_query = f"{track['name']}-{''.join(i for i in track['artists'])}"
            search_query = urllib.parse.quote(search_query)
            html = urllib.request.urlopen(
                f"https://www.youtube.com/results?search_query={search_query}")
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

            for video_id in video_ids:
                try:
                    url = "https://www.youtube.com/watch?v="+video_id
                    yt = YouTube(url)
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    audio_stream.download(download_location, "temp.mp4")
                    print(f"Downloaded Successfully : {yt.title}")
                    try:
                        os.rename(os.path.join(download_location, f"temp.mp4"), os.path.join(download_location, f"{track['name']}-{track['artists'][0]}.mp3"))
                    except:
                        try:
                            os.rename(os.path.join(download_location, f"temp.mp4"), os.path.join(download_location, f"{datetime.now().second}{datetime.now().microsecond}.mp3"))
                        except Exception as e:
                            print("Rename Error =>", e)
                    break
                except Exception as e:
                    print("Error =>", e)
                    continue

        except Exception as e:
            error_message = f"Error downloading {track} \n {e}"
            print(error_message)


def downloadSingleSong(query):
    global download_location
    query_copy = query+".mp3"
    try:
        query = urllib.parse.quote(query)
        html = urllib.request.urlopen(
            f"https://www.youtube.com/results?search_query={query}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        for video_id in video_ids:
                try:
                    url = "https://www.youtube.com/watch?v="+video_id
                    yt = YouTube(url)
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    audio_stream.download(download_location, "temp.mp4")
                    print(f"Downloaded Successfully : {yt.title}")
                    try:
                        os.rename(os.path.join(download_location, f"temp.mp4"), os.path.join(download_location, query_copy))
                    except:
                        try:
                            os.rename(os.path.join(download_location, f"temp.mp4"), os.path.join(download_location, f"{datetime.now().second}{datetime.now().microsecond}.mp3"))
                        except Exception as e:
                            print("Rename Error =>", e)
                    break
                except Exception as e:
                    print("Error =>", e)
                    continue
        
    except Exception as e:
        error_message = f"Error downloading => {e}"
        print(error_message)


# !------------------------------Download PlayList------------------------------------------------
def downloadPlayListOption():
    playlist_link = input("Enter PlayList Link : ")
    index, index2 = playlist_link.index("playlist/"), playlist_link.index("?si=")
    playlist_id = playlist_link[index+9:index2]
    tracks_obtained = getPlaylist(token=access_token, playlist_id=playlist_id)
    k=0
    name = ""
    while True:
        name = playlist_name + "-" + str(k) if k > 0 else playlist_name
        try:
            os.mkdir(os.path.join(download_location, name))
            break
        except:
            k+=1
    downloadSong(tracks_obtained, name)
    print("All Songs Are Downloaded. Thankyou!!!")


def downloadSongOption():
    song_link = input("Enter PlayList Link : ")
    index, index2 = song_link.index("track/"), song_link.index("?si=")
    song_id = song_link[index+6:index2]
    query = getSong(token=access_token, track_id=song_id)
    downloadSingleSong(query)

while 1:
    option = input("\n1.Song\n2.Playlist\n3.Exit\nEnter Your Option : ")
    if option == '1':
        downloadSongOption()
    elif option == '2':
        downloadPlayListOption()
        break
    else:
        break

print("Thank You!")