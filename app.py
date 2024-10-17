import os
import streamlit as st
import subprocess
import tempfile
from moviepy.editor import VideoFileClip

# Function to download YouTube video in high quality (1080p)
def download_youtube_video(url, quality='bestvideo[height<=1080]+bestaudio'):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
    command = f'yt-dlp -f "{quality}" --merge-output-format mp4 {url} -o "{output_path}"'

    try:
        subprocess.run(command, shell=True, check=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to download video: {e}")
        return None

# Function to extract audio and convert it to MP3
def extract_audio(input_video_path):
    audio_output_path = os.path.splitext(input_video_path)[0] + '.mp3'
    command = f'ffmpeg -i "{input_video_path}" -q:a 0 -map a "{audio_output_path}"'
    try:
        subprocess.run(command, shell=True, check=True)
        return audio_output_path
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to extract audio: {e}")
        return None

# Function to merge audio with high-quality video
def merge_audio_with_video(video_path, audio_path):
    output_video_path = os.path.join(tempfile.gettempdir(), "final_video.mp4")
    command = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -strict experimental "{output_video_path}"'
    try:
        subprocess.run(command, shell=True, check=True)
        return output_video_path
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to merge audio and video: {e}")
        return None

# Function to crop video and preserve audio
def crop_video(input_path, start_time, end_time):
    output_path = os.path.join(tempfile.gettempdir(), "cropped_video.mp4")
    try:
        with VideoFileClip(input_path) as video:
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

# Main app function
def main():
    st.title("YouTube Video Downloader and Audio Merger")

    # Initialize session state variables
    if 'video_path_1080p' not in st.session_state:
        st.session_state.video_path_1080p = None
        st.session_state.audio_path_low_quality = None
        st.session_state.final_video_path = None
        st.session_state.cropped_video_path = None

    url_1080p = st.text_input("Enter YouTube video URL (1080p):")
    url_low_quality = st.text_input("Enter YouTube video URL (Low Quality):")

    # Download high-quality video button
    if st.button("Download High-Quality Video (1080p)"):
        if url_1080p:
            temp_dir = download_youtube_video(url_1080p)
            if temp_dir:
                video_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp4')]
                if video_files:
                    st.session_state.video_path_1080p = os.path.join(temp_dir, video_files[0])
                    st.success("High-quality video downloaded successfully!")
                    st.video(st.session_state.video_path_1080p)
                else:
                    st.error("No video found to display.")
            else:
                st.error("Failed to download high-quality video.")
        else:
            st.error("Please enter a valid YouTube URL for the high-quality video.")

    # Download low-quality video button
    if st.button("Download Low-Quality Video"):
        if url_low_quality:
            temp_dir = download_youtube_video(url_low_quality)
            if temp_dir:
                video_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp4')]
                if video_files:
                    st.session_state.audio_path_low_quality = os.path.join(temp_dir, video_files[0])
                    st.success("Low-quality video downloaded successfully!")
                else:
                    st.error("No video found to display.")
            else:
                st.error("Failed to download low-quality video.")
        else:
            st.error("Please enter a valid YouTube URL for the low-quality video.")

    # Extract audio and merge with high-quality video button
    if st.button("Merge Audio with High-Quality Video"):
        if st.session_state.video_path_1080p and st.session_state.audio_path_low_quality:
            # Extract audio from low-quality video
            audio_path = extract_audio(st.session_state.audio_path_low_quality)
            if audio_path:
                # Merge extracted audio with high-quality video
                final_video_path = merge_audio_with_video(st.session_state.video_path_1080p, audio_path)
                if final_video_path:
                    st.session_state.final_video_path = final_video_path
                    st.success("Audio merged successfully!")
                    st.video(final_video_path)

                    # Download button for the final video
                    with open(final_video_path, "rb") as f:
                        st.download_button("Download Final Video", f, file_name="final_video.mp4")
        else:
            st.error("Please download both the high-quality and low-quality videos first.")

    # Show crop options only if a final video is ready
    if st.session_state.final_video_path:
        start_time_input = st.text_input("Start Time (minutes:seconds)", value="0:00")
        end_time_input = st.text_input("End Time (minutes:seconds)", value="0:10")

        # Convert to seconds
        start_time = convert_to_seconds(start_time_input)
        end_time = convert_to_seconds(end_time_input)

        # Display formatted time if conversion was successful
        if start_time is not None and end_time is not None:
            st.write(f"Start Time: {start_time_input}")
            st.write(f"End Time: {end_time_input}")

            # Crop button
            if st.button("Crop Final Video"):
                if end_time > start_time and st.session_state.final_video_path:
                    cropped_video_path = crop_video(st.session_state.final_video_path, start_time, end_time)
                    if cropped_video_path:
                        st.session_state.cropped_video_path = cropped_video_path
                        st.success("Video cropped successfully!")
                        st.video(cropped_video_path)

                        # Download button for the cropped video
                        with open(cropped_video_path, "rb") as f:
                            st.download_button("Download Cropped Video", f, file_name="cropped_video.mp4")
                else:
                    st.error("End time must be greater than start time.")

if __name__ == "__main__":
    main()
