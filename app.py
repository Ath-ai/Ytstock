import os
import streamlit as st
import subprocess
import tempfile
from moviepy.editor import VideoFileClip

# Function to download YouTube video
def download_youtube_video(url):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
    command = f'yt-dlp {url} -o "{output_path}"'
    
    try:
        subprocess.run(command, shell=True, check=True)
        return temp_dir  # Return temp directory containing the downloaded video
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

# Main app function
def main():
    st.title("YouTube Video Downloader and Cropper")

    # Store the state of whether a video has been downloaded
    if 'downloaded' not in st.session_state:
        st.session_state.downloaded = False
        st.session_state.temp_dir = None  # Store temp directory in session state
        st.session_state.cropped_video_path = None  # Store cropped video path in session state

    url = st.text_input("Enter YouTube video URL:")
    if st.button("Download"):
        if url:
            # Remove any existing cropped video before a new download
            if os.path.exists(os.path.join(tempfile.gettempdir(), "cropped_video.mp4")):
                os.remove(os.path.join(tempfile.gettempdir(), "cropped_video.mp4"))

            # Download new video
            temp_dir = download_youtube_video(url)
            if temp_dir:
                video_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mp4', '.mkv', '.webm'))]
                if video_files:
                    st.session_state.downloaded = True  # Set the downloaded flag
                    st.session_state.temp_dir = temp_dir  # Save temp_dir to session state
                    video_path = os.path.join(temp_dir, video_files[0])
                    st.video(video_path)

                    start_time = st.number_input("Start Time (in seconds)", min_value=0.0, value=0.0)
                    end_time = st.number_input("End Time (in seconds)", min_value=0.0, value=10.0)

                    if st.button("Crop Video"):
                        if end_time > start_time:
                            cropped_video_path = crop_video(video_path, start_time, end_time)
                            if cropped_video_path:
                                st.session_state.cropped_video_path = cropped_video_path  # Save the cropped video path
                                st.success("Video cropped successfully!")
                                st.video(cropped_video_path)  # Display the cropped video
                                with open(cropped_video_path, "rb") as f:
                                    st.download_button("Download Cropped Video", f, file_name="cropped_video.mp4")
                        else:
                            st.error("End time must be greater than start time.")
                else:
                    st.error("No video found to display.")
            else:
                st.error("No video found to display.")
        else:
            st.error("Please enter a valid YouTube URL.")

    # Reset state if user downloads cropped video or leaves the page
    if st.session_state.downloaded and st.button("Reset"):
        # Clean up temporary files
        if st.session_state.temp_dir:
            for filename in os.listdir(st.session_state.temp_dir):
                os.remove(os.path.join(st.session_state.temp_dir, filename))
            os.rmdir(st.session_state.temp_dir)  # Remove the temporary directory
            st.session_state.temp_dir = None  # Reset temp_dir
        st.session_state.downloaded = False  # Reset downloaded flag
        st.session_state.cropped_video_path = None  # Reset cropped video path
        st.experimental_rerun()  # Refresh the page

if __name__ == "__main__":
    main()
