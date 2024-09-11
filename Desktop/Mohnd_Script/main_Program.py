
__author__ = "Pyramids platu team"
__copyright__ = "Copyright 2024, Seitech Solutions"
__date__ = "11/8/2024"
__version__ = "1.0.0"
__status__ = "Development"
import sys
print(sys.executable)
import cloudinary
import cloudinary.api
import cloudinary.utils
import requests
import os
import time
import hashlib
import json
import multiprocessing
import psutil
import ssl
import asyncio
import mpv
import glob
import websockets

# Define SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="/home/SEI/Desktop/cert/certificate.pem", keyfile="/home/SEI/Desktop/cert/private_key.pem")
# Local directory to SD card to save the Videos.
LOCAL_VIDEO_PATH = "/home/SEI/Videos"
Videos_path = '/home/SEI/Videos'
Project_Folder = "Sei_Pym/"

#Cloud Sync Feature 
#Local directory to CHECKSUM  file for the Downloaded Videos .
CHECKSUM_FILE = os.path.join(LOCAL_VIDEO_PATH, "Operation_CHECKSUM.txt")

 # File to store the sync state.
STATE_FILE = os.path.join(LOCAL_VIDEO_PATH, "sync_state.json")

# Function to calculate a checksum for the list of downloaded  resources
def calculate_checksum(resources):

    checksum = hashlib.md5()

    for resource in sorted(resources, key=lambda x: x['public_id']):

        checksum.update(resource['public_id'].encode('utf-8'))

        checksum.update(str(resource['bytes']).encode('utf-8'))

        checksum.update(resource['created_at'].encode('utf-8'))

    return checksum.hexdigest()

# Function to download a video from Seitech Cloud
def download_video_from_cloudinary(public_id, save_path):

    try:

        # Get the video URL from Seitech Cloud
        video_url = cloudinary.utils.cloudinary_url(public_id, resource_type="video")[0]

        response = requests.get(video_url, stream=True)

        if response.status_code == 200:

            with open(save_path, 'wb') as file:

                for chunk in response.iter_content(1024):

                    file.write(chunk)

            print(f"Downloaded video: {save_path}")

        else:

            print(f"Failed to download video from {video_url}")

    except Exception as e:

        print(f"Error downloading {public_id}: {e}")


# Function to remove files that are no longer present in Seitech Cloud
def remove_old_files(existing_files):

    local_files = set(os.listdir(LOCAL_VIDEO_PATH))

    for file in local_files:

        if file not in existing_files and file != os.path.basename(CHECKSUM_FILE) and file != os.path.basename(STATE_FILE):

            os.remove(os.path.join(LOCAL_VIDEO_PATH, file))

            print(f"Removed old video: {file}")

# Function to save the sync state

def save_sync_state(sync_state):

    with open(STATE_FILE, 'w') as f:

        json.dump(sync_state, f)

# Function to load the sync state
def load_sync_state():

    if os.path.exists(STATE_FILE):

        with open(STATE_FILE, 'r') as f:

            return json.load(f)

    return {}

# Function to sync videos from a specific folder in Seitech Cloud

def sync_videos_from_folder(folder_name):

    try:

        resources = cloudinary.api.resources(type="upload", prefix=folder_name, resource_type="video")['resources']

        new_checksum = calculate_checksum(resources)

        # Load the previous checksum and sync state if they exist
        old_checksum = None

        sync_state = load_sync_state()

        if os.path.exists(CHECKSUM_FILE):

            with open(CHECKSUM_FILE, 'r') as f:

                old_checksum = f.read().strip()

        # If checksum is different or file is missing, sync the folder
        if new_checksum != old_checksum:
            
            # Save the new checksum
            with open(CHECKSUM_FILE, 'w') as f:

                f.write(new_checksum)

            # Track the files currently in Seitech cloud
            cloudinary_files = set()

            # Download the updated or new files
            for resource in resources:

                public_id = resource['public_id']

                file_name = os.path.basename(public_id) + '.' + resource['format']

                save_path = os.path.join(LOCAL_VIDEO_PATH, file_name)

                cloudinary_files.add(file_name)

                # Check if this file was already partially or fully downloaded
                if file_name not in sync_state or sync_state[file_name] != 'downloaded':

                    download_video_from_cloudinary(public_id, save_path)

                    sync_state[file_name] = 'downloaded'

                    save_sync_state(sync_state)

            # Remove old files that are no longer in Seitech ccloud
            remove_old_files(cloudinary_files)

            # Clear the sync state after a successful sync
            sync_state.clear()

            save_sync_state(sync_state)

        else:

            print("No changes detected. Skip the operation .")

    except Exception as e:

        print(f"Error syncing resources: {e}")

'''***************************************************************'''
# Ads Feature
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

#*********************************************************************#
#Server Feature

async def hello(websocket):
    try:
        while True:  # Continuous loop to handle multiple messages
            data = await websocket.recv()
            print(f'Server Received: {data}')
            greeting = f'{data}!'
            await websocket.send(greeting)
            print(f'Server Sent: {greeting}')
    except websockets.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"An error occurred: {e}")

async def server_main():
    async with websockets.serve(hello, "192.168.25.143",443, ssl=ssl_context, ping_interval=60, ping_timeout=60):
        await asyncio.Future()  # run forever

#*************************************************************#
def task1():
    print(f"Task 1 started on process ID: {os.getpid()}")
    # Set affinity to core 0
    psutil.Process(os.getpid()).cpu_affinity([0])
  #  while True:
    print(f"Task 1 running on core: {psutil.Process().cpu_affinity()}")
    Play_Ads(Videos_path)
	

def task2():
    print(f"Task 2 started on process ID: {os.getpid()}")
    # Set affinity to core 1
    psutil.Process(os.getpid()).cpu_affinity([1])
   # while True:
    print(f"Task 2 running on core: {psutil.Process().cpu_affinity()}")
    sync_videos_from_folder(Project_Folder)
    time.sleep(30)

def task3():
    print(f"Task 2 started on process ID: {os.getpid()}")
    # Set affinity to core 2
    psutil.Process(os.getpid()).cpu_affinity([2])
  #  while True:
    print(f"Task 3 started on process ID: {os.getpid()}")
    print(f"Task 3 running on core: {psutil.Process().cpu_affinity()}")
    asyncio.run(server_main())
def main():
    while True:
        # Start the timer
     #   start_time = time.perf_counter()

        # Create processes for each task
        p1 = multiprocessing.Process(target=task1)
        p2 = multiprocessing.Process(target=task2)
        p3 = multiprocessing.Process(target=task3)

        # Start the processes
        p1.start()
        p2.start()
        p3.start()

        # Wait for all processes to finish
        p1.join()
        p2.join()
        p3.join()


if __name__ == '__main__':
    asyncio.run(main())
