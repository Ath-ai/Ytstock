import os
import streamlit as st
import subprocess
import tempfile
from moviepy.editor import VideoFileClip

# Function to download YouTube video
def download_youtube_video(url):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
    command = f'yt-dlp {url} -o "{output_path}"'
    
    try:
        subprocess.run(command, shell=True, check=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to download video: {e}")
        return None

# Function to crop video
def crop_video(input_path, start_time, end_time):
    output_path = os.path.join(tempfile.gettempdir(), "cropped_video.mp4")
    try:
        with VideoFileClip(input_path) as video:
            cropped_video = video.subclip(start_time, end_time)
            cropped_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        return output_path
    except Exception as e:
        st.error(f"Failed to crop the video: {e}")
        return None

# Function to format time
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes} minutes {seconds} seconds"

# Main app function
def main():
    st.title("YouTube Video Downloader and Cropper")

    # Initialize session state variables
    if 'downloaded' not in st.session_state:
        st.session_state.downloaded = False
        st.session_state.temp_dir = None
        st.session_state.cropped_video_path = None
        st.session_state.video_path = None

    url = st.text_input("Enter YouTube video URL:")
    
    # Download button
    if st.button("Download"):
        if url:
            # Clean up previous files if they exist
            if st.session_state.cropped_video_path and os.path.exists(st.session_state.cropped_video_path):
                os.remove(st.session_state.cropped_video_path)

            # Download the video
            temp_dir = download_youtube_video(url)
            if temp_dir:
                video_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mp4', '.mkv', '.webm'))]
                if video_files:
                    st.session_state.downloaded = True
                    st.session_state.temp_dir = temp_dir
                    st.session_state.video_path = os.path.join(temp_dir, video_files[0])
                    st.video(st.session_state.video_path)
                else:
                    st.error("No video found to display.")
            else:
                st.error("No video found to display.")
        else:
            st.error("Please enter a valid YouTube URL.")

    # Show crop options only if a video is downloaded
    if st.session_state.downloaded:
        start_time = st.number_input("Start Time (in seconds)", min_value=0.0, value=0.0)
        end_time = st.number_input("End Time (in seconds)", min_value=0.0, value=10.0)

        # Display formatted time
        st.write(f"Start Time: {format_time(start_time)}")
        st.write(f"End Time: {format_time(end_time)}")

        # Crop button
        if st.button("Crop Video"):
            if end_time > start_time and st.session_state.video_path:
                cropped_video_path = crop_video(st.session_state.video_path, start_time, end_time)
                if cropped_video_path:
                    st.session_state.cropped_video_path = cropped_video_path
                    st.success("Video cropped successfully!")
                    st.video(cropped_video_path)

                    # Download button for the cropped video
                    with open(cropped_video_path, "rb") as f:
                        st.download_button("Download Cropped Video", f, file_name="cropped_video.mp4")
            else:
                st.error("End time must be greater than start time.")

    # Reset button to clear state
    if st.button("Reset"):
        # Cleanup session state
        if st.session_state.temp_dir:
            for filename in os.listdir(st.session_state.temp_dir):
                os.remove(os.path.join(st.session_state.temp_dir, filename))
            os.rmdir(st.session_state.temp_dir)
            st.session_state.temp_dir = None
        st.session_state.downloaded = False
        st.session_state.cropped_video_path = None
        st.session_state.video_path = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()
