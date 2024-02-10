# Copyright (c) 2024 Andor Zoltán Fülöp | All rights reserved!

################################################################################################
##################### Fill out these global variables with your own values #####################
################################################################################################
YOUTUBE_API_KEY = ''                                        # Your YouTube API key  
PODCASTVIDEO_POOL_PATH = './Videos/PodcastVideoPool.txt'    # Text file containing the links to the podcast videos
GTA_VIDEO_POOL_PATH = './Videos/GtaGameplayPool.txt'        # Text file containing the links to the GTA gameplay videos
RAW_VIDEO_PATH = './Videos/Raw'                             # The path where the raw videos will be stored
EDITED_VIDEO_PATH = './Videos/Final'                        # The path where the edited videos will be stored
################################################################################################
################################################################################################

# Importing libraries
import re
import sys
import time
import subprocess
import os, os.path
from googleapiclient.discovery import build

# Main function
def main():
    if not os.path.exists(f"{RAW_VIDEO_PATH}/GTA"):
        os.makedirs(f"{RAW_VIDEO_PATH}/GTA")
    if not os.path.exists(f"{RAW_VIDEO_PATH}/Podcast"):
        os.makedirs(f"{RAW_VIDEO_PATH}/Podcast")
    if not os.path.exists(EDITED_VIDEO_PATH):
        os.makedirs(EDITED_VIDEO_PATH)

    video_amount = int(sys.argv[1])
    gta_video_amount = len([name for name in os.listdir(f"{RAW_VIDEO_PATH}/GTA") if os.path.isfile(os.path.join(f"{RAW_VIDEO_PATH}/GTA", name))])
    podcast_video_amount = len([name for name in os.listdir(f"{RAW_VIDEO_PATH}/Podcast") if os.path.isfile(os.path.join(f"{RAW_VIDEO_PATH}/Podcast", name))])
    
    if video_amount > gta_video_amount:
        gta_video_links = get_video_link_pool(GTA_VIDEO_POOL_PATH)
        for video in gta_video_links:
            if "[USED]" in video: continue

            duration = get_video_duration(get_youtube_video_id(video))
            for i in range(duration // 60):
                download_video_part(video, f'{i}:00', f'{i + 1}:00', f'{RAW_VIDEO_PATH}/GTA/{get_youtube_video_id(video)}_{i}')
                time.sleep(1)
            
            temp = gta_video_links
            temp[temp.index(video)] = f"[USED]{video}"
            update_video_link_pool(GTA_VIDEO_POOL_PATH, temp)

            gta_video_amount = len([name for name in os.listdir(f"{RAW_VIDEO_PATH}/GTA") if os.path.isfile(os.path.join(f"{RAW_VIDEO_PATH}/GTA", name))])
            if video_amount <= gta_video_amount:
                break            
    
    if video_amount > podcast_video_amount:
        podcast_video_links = get_video_link_pool(PODCASTVIDEO_POOL_PATH)
        for video in podcast_video_links:
            if "[USED]" in video: continue

            duration = get_video_duration(get_youtube_video_id(video))
            for i in range(10, duration // 60, 10):
                if i < 60:
                    minutes, seconds = divmod(i * 60, 60)
                    start_time = f'{int(minutes):02d}:{int(seconds):02d}'
                else:
                    hours, minutes = divmod(i, 60)
                    start_time =f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'

                if i < 60:
                    minutes, seconds = divmod((i + 1) * 60, 60)
                    end_time = f'{int(minutes):02d}:{int(seconds):02d}'
                else:
                    hours, minutes = divmod(i + 1, 60)
                    end_time =f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'
                download_video_part(video, start_time, end_time, f'{RAW_VIDEO_PATH}/Podcast/{get_youtube_video_id(video)}_{i}')
                time.sleep(1)
            
            temp = podcast_video_links
            temp[temp.index(video)] = f"[USED]{video}"
            update_video_link_pool(PODCASTVIDEO_POOL_PATH, temp)

            podcast_video_amount = len([name for name in os.listdir(f"{RAW_VIDEO_PATH}/Podcast") if os.path.isfile(os.path.join(f"{RAW_VIDEO_PATH}/Podcast", name))])
            if video_amount <= podcast_video_amount:
                break
    
    gta_videos = [name for name in os.listdir(f"{RAW_VIDEO_PATH}/GTA") if os.path.isfile(os.path.join(f"{RAW_VIDEO_PATH}/GTA", name))]
    podcast_videos = [name for name in os.listdir(f"{RAW_VIDEO_PATH}/Podcast") if os.path.isfile(os.path.join(f"{RAW_VIDEO_PATH}/Podcast", name))]
    for i in range(video_amount):
        combine_videos(f"{RAW_VIDEO_PATH}/Podcast/{podcast_videos[i]}", f"{RAW_VIDEO_PATH}/GTA/{gta_videos[i]}", f"{RAW_VIDEO_PATH}/Podcast/{podcast_videos[i]}".replace(".mp4", "").split("_")[1])
        transcribe_video(EDITED_VIDEO_PATH + "/" + f"{RAW_VIDEO_PATH}/Podcast/{podcast_videos[i]}".replace(".mp4", "").split("_")[1])
        os.remove(f"{RAW_VIDEO_PATH}/Podcast/{podcast_videos[i]}")
        os.remove(f"{RAW_VIDEO_PATH}/GTA/{gta_videos[i]}")


# Function to get the video links from the pool
def get_video_link_pool(filepath):
    with open(filepath, 'r') as file:
        return file.readlines()


# Function to update the video link pool
def update_video_link_pool(filepath, video_links):
    with open(filepath, 'w') as file:
        file.writelines(video_links)


# Function to get the video id from the video link
def get_youtube_video_id(url):
    match = re.search(r"(?:youtube\.com/(?:[-\w]+\?v=|embed/|v/)?)([-\w]+)", url)
    if match:
        return match.group(1)
    else:
        return None


# Function to download a video part
def download_video_part(url, start_time, end_time, save_location):
    video_url, audio_url = subprocess.check_output(f'yt-dlp.exe -g {url}', shell=True).decode().strip().split('\n')    
    cmd = f'ffmpeg -ss {start_time} -to {end_time} -i "{video_url}" -ss {start_time} -to {end_time} -i "{audio_url}" -c copy {save_location}.mp4'
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    cmd = f'ffmpeg -i {save_location}.mp4 -vf scale=1920:1080 {save_location}[EDITED].mp4'
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    cmd = f'ffmpeg -i {save_location}[EDITED].mp4 -vf fps=fps=30 {save_location}[EDITED-FINAL].mp4'
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    os.remove(f'{save_location}.mp4')
    os.remove(f'{save_location}[EDITED].mp4')
    os.rename(f'{save_location}[EDITED-FINAL].mp4', f'{save_location}.mp4')


# Function to get the video duration
def get_video_duration(video_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().list(
        part='contentDetails',
        id=video_id
    )
    response = request.execute()   
    duration = response['items'][0]['contentDetails']['duration'].replace('PT', '').replace('H', ':').replace('M', ':').replace('S', '').split(':')[::-1] 
    duration_in_seconds = 0
    for i in range(len(duration)):
        duration_in_seconds += int(duration[i]) * (60 ** i)
    return duration_in_seconds - 1


# Function to combine the videos
def combine_videos(top_video, bottom_video, title):
    cmd = f'ffmpeg -i {top_video} -i {bottom_video} -filter_complex vstack {EDITED_VIDEO_PATH}/{title}[MERGED].mp4'
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    cmd = f'ffmpeg -i {EDITED_VIDEO_PATH}/{title}[MERGED].mp4 -vf scale=1706:1920 {EDITED_VIDEO_PATH}/{title}[SCALED].mp4'
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    cmd = f'ffmpeg -i {EDITED_VIDEO_PATH}/{title}[SCALED].mp4 -vf "crop=1080:1920:(1706-1080)/2:0" {EDITED_VIDEO_PATH}/{title}.mp4'
    subprocess.call(cmd, shell=True)
    time.sleep(1)
    os.remove(f'{EDITED_VIDEO_PATH}/{title}[MERGED].mp4')
    os.remove(f'{EDITED_VIDEO_PATH}/{title}[SCALED].mp4')


# Function to transcribe the final video
def transcribe_video(video_path):
    audio_path = f"{video_path}.mp3"
    video_path = f"{video_path}.mp4"
    directory, filename = os.path.split(video_path.replace(".mp4", ""))
    subtitle_path = os.path.join(directory, "").replace("\\", "/")

    cmd = f"ffmpeg -y -i {video_path} {audio_path}"
    subprocess.run(cmd, check=True)

    cmd = f"whisper {audio_path} --model large-v2 --language English --word_timestamps True --max_line_count 1 --max_line_width 15 --output_format srt --output_dir {subtitle_path}"
    subprocess.run(cmd, check=True)

    cmd = f"ffmpeg -i {video_path} -vf subtitles={subtitle_path}{filename}.srt:force_style='Alignment=10,Fontsize=20,Outline=1.5,Bold=1,Shadow=0,MarginV=0,MarginL=10,MarginR=10' {subtitle_path}{filename}[TRANSCRIPTED].mp4"
    subprocess.run(cmd, check=True)

    os.remove(video_path)
    os.remove(audio_path)
    os.remove(f"{subtitle_path}{filename}.srt")
    os.rename(f"{subtitle_path}{filename}[TRANSCRIPTED].mp4", video_path)


if __name__ == '__main__':
    main()