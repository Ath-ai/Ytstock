import os
import subprocess
import streamlit as st
import tempfile

# Auto-install missing dependencies
try:
    from moviepy.editor import VideoFileClip
except ModuleNotFoundError:
    subprocess.run(["pip", "install", "moviepy"], stdout=subprocess.PIPE, text=True)
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

# Main app function
def main():
    st.title("YouTube Video Downloader and Cropper")

    url = st.text_input("Enter YouTube video URL:")
    quality = st.selectbox("Select Video Quality", ["best", "720p", "480p", "360p"])
    quality_map = {"best": "2160", "720p": "720", "480p": "480", "360p": "360"}

    if st.button("Download"):
        if url:
            temp_dir = download_youtube_video(url, quality_map[quality])
            if temp_dir:
                st.session_state.video_path = os.path.join(
                    temp_dir, os.listdir(temp_dir)[0]
                )
                st.video(st.session_state.video_path)
            else:
                st.error("Failed to download video.")
        else:
            st.error("Please enter a valid YouTube URL.")

    if st.button("Reset"):
        if st.session_state.get("video_path"):
            os.remove(st.session_state.video_path)
            st.session_state.video_path = None
        st.experimental_rerun()


if __name__ == "__main__":
    main()
