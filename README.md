# TikTok Video Creator
The TikTok Video Creator is a powerful program designed for content creators who want to enhance their TikTok videos with a unique blend of podcast discussions and exciting GTA gameplay. This tool automates the process of extracting 1-minute clips from specified YouTube videos, seamlessly merging them, and generating a corresponding transcript.

### Requirements
To use this program, ensure you have downloaded [ffmpeg](https://ffmpeg.org/download.html) and [yt-dlp](https://github.com/yt-dlp/yt-dlp) and that they are included in the `PATH` environment variable. After that, install the necessary Python dependencies:
```bash
pip install -r requirements.txt
```
### Usage
1. Create two text files that will contain the URLs for podcasts and GTA gameplays. Ensure that each link is on a new line. (Accepted link format example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
2. Assign a value to each global variable located at the top of the Python script.
3. Run the program from the CMD:
    ```bash
    python TikTokVideoCreator.py <HOW_MANY_VIDEOS_YOU_WANT>
    ```
When specifying the number of videos, ensure that there is enough material for the final videos. (GTA videos are sliced every minute, and podcasts have a 1-minute clip every 10 minutes.)