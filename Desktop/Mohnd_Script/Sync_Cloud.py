

__author__ = "Mohnd Elhossin"
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

# Configuretion Of the Cloudinary Platform

cloudinary.config(

    cloud_name=os.getenv('PYMSERVER_CLOUD_NAME') , # Name of the cloud Profile contain the needed data .

    api_key=os.getenv('PYMSERVER_CLOUD_API_KEY'),        # Sei Cloud Profile API Key .

    api_secret=os.getenv('PYMSERVER_CLOUD_API_SECRET')   # Sei cloud API SECRET  (like Authentcation ).

)

# Local directory to SD card to save the Videos.
LOCAL_VIDEO_PATH = "/home/SEI/Videos"

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

# Main execution

if __name__ == "__main__":
	
    # Replace with the Pyramids project folder name
    Project_Folder = "Sei_Pym/"

    while True:

        sync_videos_from_folder(Project_Folder)
      # Wait for 15s  before running again
        time.sleep(15)
