import streamlit as st
import os
import subprocess
import tempfile
from moviepy.editor import VideoFileClip

# Function to download YouTube video
def download_youtube_video(url, download_path):
    command = f'yt-dlp {url} -o "{download_path}/%(title)s.%(ext)s"'
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to download video: {e}")
        return False

# Function to crop video
def crop_video(input_path, start_time, end_time, output_path):
    try:
        with VideoFileClip(input_path) as video:
            cropped_video = video.subclip(start_time, end_time)
            cropped_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            return True
    except Exception as e:
        st.error(f"Failed to crop the video: {e}")
        return False

# Streamlit app interface
st.title("YouTube Video Crop and Download")

# Input fields for YouTube URL and cropping times
url = st.text_input("Enter YouTube video URL:")
start_time = st.number_input("Start Time (in seconds):", min_value=0.0, format="%.2f")
end_time = st.number_input("End Time (in seconds):", min_value=0.0, format="%.2f")

# Button to initiate the download and crop process
if st.button("Download and Crop Video"):
    # Create a temporary directory to store files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define paths
        download_path = os.path.join(temp_dir, "downloaded_video.mp4")
        cropped_path = os.path.join(temp_dir, "cropped_video.mp4")

        # Download the video
        if download_youtube_video(url, temp_dir):
            # Crop the video
            if crop_video(download_path, start_time, end_time, cropped_path):
                # Provide a download link for the cropped video
                with open(cropped_path, "rb") as f:
                    st.download_button("Download Cropped Video", f, file_name="cropped_video.mp4")

# Note: The temporary files will be automatically deleted when leaving the `with` block
