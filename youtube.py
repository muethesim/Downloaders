from pytube import YouTube, Playlist
import os
from datetime import datetime
from moviepy.editor import *

folder_name = "Youtube Downloads"

download_path = os.path.join(os.getcwd(), folder_name)
if not os.path.exists(download_path):
    os.mkdir(folder_name)
    print("There Was No Folder Present in the name. Automatically Created...")
    

def getYT(url):
    return YouTube(url)

def getQuality(yt):
    try:
        yt_stream = yt.streams
        resolutions = []
        for i in yt_stream:
            if i.resolution not in resolutions:
                resolutions.append(i.resolution)
        if None in resolutions: 
            resolutions.remove(None)
        resolutions = sorted(resolutions)
        resolutions.append("Audio")
        while 1:
            try:
                for i, j in enumerate(resolutions):
                    print(f"{i+1}.{j}")
                quality_index = int(input("Select Any Option : "))
                if quality_index < 1 or quality_index > len(resolutions):
                    print("Invalid Input!!! Stopping The Program...")
                    return
                break
            except:
                print("Invalid Option")
        quality = resolutions[quality_index-1]
    except Exception as e:
        print(e)
    return quality

def downloadVideo(yt, quality):
    print(f"Starting Download : {yt.title}")
    try:
        yt_stream = yt.streams
        if quality == "Audio":
            video_stream = yt_stream.filter(only_audio=True).first()
            video_stream.download(download_path, "temp.mp4")
            try:
                os.rename(os.path.join(download_path, "temp.mp4"), os.path.join(download_path, f"{video_stream.title}.mp3"))
            except:
                try:
                    os.rename(os.path.join(download_path, f"temp.mp4"), os.path.join(download_path, f"{datetime.now().second+datetime.now().microsecond}.mp3"))
                except Exception as e:
                    print("Rename Error =>", e)
        else:
            video_stream = yt_stream.filter(res=quality, progressive=True).first()

            if video_stream:
                video_stream.download(download_path)
            else:
                video_stream = yt_stream.filter(progressive=True).first()
                if video_stream:
                    video_stream.download(download_path)
                else:
                    video_stream = yt_stream.filter(res=quality).first()
                    audio_stream = yt_stream.filter(only_audio=True).first()

                    if video_stream == None:
                        video_stream = yt_stream.filter().first()
                    if audio_stream == None:
                        video_stream.download(download_path)
                        return

                    video_path = video_stream.download(download_path, filename='video.mp4')
                    audio_path = audio_stream.download(download_path, filename='temp.mp4')
                    video_clip = VideoFileClip(video_path)
                    audio_clip = AudioFileClip(audio_path)

                    final_clip = video_clip.set_audio(audio_clip)
                    try:
                        final_clip.write_videofile(os.path.join(download_path, f"{yt.title}.mp4"))
                    except:
                        final_clip.write_videofile(os.path.join(download_path, f"{datetime.now().second+datetime.now().microsecond}.mp4"))
                    os.remove(video_path)
                    os.remove(audio_path)

        print(f"File Downloaded : {yt.title}\n")
    except:
        print("Error")

def downloadPlaylist():
    global download_path
    url = input("Enter The Url to Playlist. Enter -1 To Exit : ")
    if url != '-1':
        pl = Playlist(url)
        k=0
        name = ""
        while True:
            name = pl.title + "-" + str(k) if k > 0 else pl.title
            try:
                os.mkdir(os.path.join(download_path, name))
                break
            except:
                k+=1
        download_path = os.path.join(download_path, name)
        qualities = ["144p", "240p", "360p", "480p", "720p", "1080p", "Audio"]
        while 1:
            try:
                for i, j in enumerate(qualities):
                    print(f"{i+1}.{j}")
                quality_index = int(input("Select Any Option : "))
                if quality_index < 1 or quality_index > len(qualities):
                    print("Invalid Input!!! Stopping The Program...")
                    return
                break
            except:
                print("Invalid Option")
        quality = qualities[quality_index-1]
        print("Note: If The quality Mentioned is Not Available for the video, It will download a video of 360p by default.")
        for video_url in pl:
            yt = getYT(video_url)
            downloadVideo(yt, quality)
    else:
        return


option = input("1.Playlist\n2.Video\nEnter Option:")
if option == '1':
    downloadPlaylist()
elif option == '2':
    while 1:
        url = input("Enter The Url to Video. Enter -1 To Exit : ")
        if url != '-1':
            yt = getYT(url)
            video = getQuality(yt)
            downloadVideo(yt, video)
        else:
            break

print("Thank You For Using!!!")