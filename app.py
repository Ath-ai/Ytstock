import os
import re
import subprocess
from moviepy.editor import VideoFileClip
import streamlit as st

# Directory for downloads
DOWNLOAD_DIR = './downloads'

# Create the download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to download YouTube video using yt-dlp
def download_youtube_video(url):
    # Sanitize URL by removing query parameters (everything after '?')
    clean_url = re.sub(r'\?.*$', '', url)
    
    try:
        # yt-dlp command to download the video
        command = f'yt-dlp {clean_url} -o "{DOWNLOAD_DIR}/%(title)s.%(ext)s"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

        # Check for output files in the download directory
        video_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".mp4")]
        if video_files:
            video_file_path = os.path.join(DOWNLOAD_DIR, video_files[0])
            return video_file_path
        else:
            return None
    except subprocess.CalledProcessError as e:
        # Capture detailed error message
        st.error(f"Download failed: {e.output or e.stderr}")
        return None

# Function to crop video using MoviePy
def crop_video(input_path, start_time, end_time):
    try:
        # Load video file
        clip = VideoFileClip(input_path)
        
        # Crop the video by selecting the start and end times
        cropped_clip = clip.subclip(start_time, end_time)
        
        # Generate the output file name
        output_path = os.path.join(DOWNLOAD_DIR, f"cropped_{os.path.basename(input_path)}")
        
        # Write the cropped video to a new file
        cropped_clip.write_videofile(output_path, codec='libx264')
        
        return output_path
    except Exception as e:
        st.error(f"Failed to crop the video: {str(e)}")
        return None

# Streamlit Interface
def main():
    st.title("YouTube Video Downloader and Cropper")
    
    # User input for YouTube URL
    video_url = st.text_input("Enter YouTube video URL:")
    
    # Download button
    if st.button("Download Video"):
        if video_url:
            video_path = download_youtube_video(video_url)
            if video_path:
                st.success(f"Video downloaded successfully: {video_path}")
                st.video(video_path)
            else:
                st.error("Failed to download video.")
    
    # Show cropper options if a video was downloaded
    if os.listdir(DOWNLOAD_DIR):
        st.subheader("Crop the downloaded video")
        
        # Allow the user to specify start and end times
        start_time = st.number_input("Start time (seconds)", min_value=0)
        end_time = st.number_input("End time (seconds)", min_value=0)
        
        # Get the latest downloaded video for cropping
        downloaded_videos = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".mp4")]
        if downloaded_videos:
            latest_video = os.path.join(DOWNLOAD_DIR, downloaded_videos[-1])
            
            if st.button("Crop Video"):
                if end_time > start_time:
                    cropped_path = crop_video(latest_video, start_time, end_time)
                    if cropped_path:
                        st.success(f"Video cropped successfully: {cropped_path}")
                        st.video(cropped_path)
                else:
                    st.error("End time must be greater than start time.")

if __name__ == "__main__":
    main()
