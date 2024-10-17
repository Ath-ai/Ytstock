import streamlit as st
import subprocess
import os
from moviepy.editor import VideoFileClip

# Function to download video using yt-dlp
def download_video(url, quality):
    # Construct command to download video with yt-dlp
    command = f"yt-dlp -f '{quality}' -o './downloads/%(title)s.%(ext)s' {url}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

# Function to crop video
def crop_video(input_path, start_time, end_time):
    output_path = f'./downloads/cropped_{os.path.basename(input_path)}'
    clip = VideoFileClip(input_path).subclip(start_time, end_time)
    clip.write_videofile(output_path)
    return output_path

# Streamlit UI
st.title("YouTube Video Downloader and Cropper")

url = st.text_input("Enter YouTube Video URL:")
quality = st.selectbox("Select Quality", ["best", "720p", "1080p"])

if st.button("Download Video"):
    if url:
        with st.spinner("Downloading video..."):
            result = download_video(url, quality)
            if result.returncode == 0:
                st.success("Video downloaded successfully!")
            else:
                st.error(f"Failed to download video: {result.stderr}")

start_time = st.text_input("Start Time (in seconds):", "0")
end_time = st.text_input("End Time (in seconds):", "10")

if st.button("Crop Video"):
    input_path = './downloads/' + os.path.basename(url) + '.mp4'
    if os.path.exists(input_path):
        with st.spinner("Cropping video..."):
            cropped_video = crop_video(input_path, float(start_time), float(end_time))
            st.video(cropped_video)
    else:
        st.error("Video file does not exist.")
