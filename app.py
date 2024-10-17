import streamlit as st
import imageio_ffmpeg as ffmpeg
import tempfile
import os
from moviepy.editor import VideoFileClip

# Function to crop the video
def crop_video(input_path, start_time, end_time):
    output_path = os.path.join(tempfile.gettempdir(), "cropped_video.mp4")
    with VideoFileClip(input_path) as video:
        cropped_video = video.subclip(start_time, end_time)
        cropped_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    return output_path

# Function to process the video and get duration
def process_video(video_path):
    try:
        duration = ffmpeg.get_duration(video_path)
        return duration
    except Exception as e:
        st.error(f"Error accessing FFmpeg: {e}")
        return None

def main():
    st.title("Video Cropper with FFmpeg")

    uploaded_file = st.file_uploader("Upload a video file (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])
    
    if uploaded_file is not None:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_file_path = tmp_file.name
        
        # Process the video to get its duration
        duration = process_video(temp_file_path)
        if duration is not None:
            st.write(f"Video Duration: {duration:.2f} seconds")

            # Input for start and end time for cropping
            start_time_input = st.text_input("Start Time (minutes:seconds)", value="0:00")
            end_time_input = st.text_input("End Time (minutes:seconds)", value=f"{int(duration // 60)}:{int(duration % 60)}")
            
            # Convert input to seconds
            def convert_to_seconds(time_str):
                minutes, seconds = map(float, time_str.split(':'))
                return minutes * 60 + seconds
            
            if st.button("Crop Video"):
                start_time = convert_to_seconds(start_time_input)
                end_time = convert_to_seconds(end_time_input)

                if start_time < end_time and end_time <= duration:
                    cropped_video_path = crop_video(temp_file_path, start_time, end_time)
                    st.success("Video cropped successfully!")
                    st.video(cropped_video_path)

                    # Download button for the cropped video
                    with open(cropped_video_path, "rb") as f:
                        st.download_button("Download Cropped Video", f, file_name="cropped_video.mp4")
                else:
                    st.error("Invalid time range. Ensure end time is greater than start time and within video duration.")

        # Cleanup temporary file after processing
        os.remove(temp_file_path)

if __name__ == "__main__":
    main()
