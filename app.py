import os
import subprocess
import streamlit as st
import tempfile

# Auto-install missing dependencies
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    subprocess.run(["pip", "install", "moviepy"], check=True)
    from moviepy.editor import VideoFileClip


# Function to download YouTube video with selected quality
def download_youtube_video(url, quality="best"):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
    command = f'yt-dlp -f "bestvideo[height<={quality}]+bestaudio/best" {url} -o "{output_path}"'
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
    st.title("YouTube Video Downloader and Cropper")

    if 'downloaded' not in st.session_state:
        st.session_state.downloaded = False
        st.session_state.temp_dir = None
        st.session_state.cropped_video_path = None
        st.session_state.video_path = None

    url = st.text_input("Enter YouTube video URL:")
    quality = st.selectbox("Select Video Quality", ["best", "720p", "480p", "360p"])
    quality_map = {"best": "2160", "720p": "720", "480p": "480", "360p": "360"}

    if st.button("Download"):
        if url:
            if st.session_state.cropped_video_path and os.path.exists(st.session_state.cropped_video_path):
                os.remove(st.session_state.cropped_video_path)

            temp_dir = download_youtube_video(url, quality_map[quality])
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

    if st.session_state.downloaded:
        start_time_input = st.text_input("Start Time (minutes:seconds)", value="0:00")
        end_time_input = st.text_input("End Time (minutes:seconds)", value="0:10")

        start_time = convert_to_seconds(start_time_input)
        end_time = convert_to_seconds(end_time_input)

        if start_time is not None and end_time is not None:
            st.write(f"Start Time: {start_time} seconds")
            st.write(f"End Time: {end_time} seconds")

            if st.button("Crop Video"):
                if end_time > start_time and st.session_state.video_path:
                    cropped_video_path = crop_video(st.session_state.video_path, start_time, end_time)
                    if cropped_video_path:
                        st.session_state.cropped_video_path = cropped_video_path
                        st.success("Video cropped successfully!")
                        st.video(cropped_video_path)

                        with open(cropped_video_path, "rb") as f:
                            st.download_button("Download Cropped Video", f, file_name="cropped_video.mp4")
                else:
                    st.error("End time must be greater than start time.")

    if st.button("Reset"):
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
