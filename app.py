import os
import streamlit as st
import subprocess
import tempfile
from moviepy.editor import VideoFileClip

# Function to download YouTube video in high quality (1080p) and combine video/audio
def download_youtube_video(url):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
    # Download best video and best audio, merge into one file
    command = f'yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" --merge-output-format mp4 {url} -o "{output_path}"'

    try:
        subprocess.run(command, shell=True, check=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to download video: {e}")
        return None

# Function to crop video and preserve audio
def crop_video(input_path, start_time, end_time):
    output_path = os.path.join(tempfile.gettempdir(), "cropped_video.mp4")
    try:
        with VideoFileClip(input_path) as video:
            # Crop video and keep the audio
            cropped_video = video.subclip(start_time, end_time)
            cropped_video.write_videofile(output_path, codec='libx264', audio_codec='aac', preset='fast', threads=4)
        return output_path
    except Exception as e:
        st.error(f"Failed to crop the video: {e}")
        return None

# Function to convert "minutes:seconds" to total seconds
def convert_to_seconds(time_str):
    if time_str:
        try:
            minutes, seconds = map(float, time_str.split(':'))
            return minutes * 60 + seconds
        except ValueError:
            st.error("Invalid time format. Please use 'minutes:seconds' format (e.g., '2:22').")
            return None
    return 0

# Function to format time for display
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
        start_time_input = st.text_input("Start Time (minutes:seconds)", value="0:00")
        end_time_input = st.text_input("End Time (minutes:seconds)", value="0:10")

        # Convert to seconds
        start_time = convert_to_seconds(start_time_input)
        end_time = convert_to_seconds(end_time_input)

        # Display formatted time if conversion was successful
        if start_time is not None and end_time is not None:
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
