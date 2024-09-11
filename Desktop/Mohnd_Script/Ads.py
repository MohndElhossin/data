

__author__ = "Mohnd Elhossin"
__copyright__ = "Copyright 2024, Seitech Solutions"
__date__ = "11/8/2024"
__version__ = "1.0.0"
__status__ = "Development"

import mpv
import os
import glob


# Specify Path of the videos
Videos_path = '/home/SEI/Videos'
# List of video file extensions to look for
video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.flv']
#Create mpv media player 
player = mpv.MPV()
def Play_Ads(folder_path):

# List all videos in Pyramids local Storage 
    video_files = []
    for extension in video_extensions:
        video_files.extend(glob.glob(os.path.join(folder_path, extension)))

        for video in video_files:

            video_path = os.path.join(folder_path, video)
            # Play the media
            player.play(video_path)
            
            # Wait until the video finishes
            player.wait_until_playing()
            player.wait_for_playback()


 

if __name__ == "__main__":
    while True:
        Play_Ads(Videos_path)

