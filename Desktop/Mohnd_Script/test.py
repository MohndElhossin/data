import os
import subprocess
# Folder containing your video files
video_folder = "/home/SEI/Videos"
# Function to play video using omxplayer
def play_video(video_path):
   subprocess.run(["omxplayer", video_path])
# List all video files in the folder
video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mkv'))]
# Loop to play all videos one by one
for video_file in video_files:
   video_path = os.path.join(video_folder, video_file)
   print(f"Playing: {video_file}")
   play_video(video_path)
   # Ask user whether to continue or stop
   user_input = input("Press Enter to play the next video or type 'q' to quit: ")
   if user_input.lower() == 'q':
       break
