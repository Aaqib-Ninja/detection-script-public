import streamlit as st
from video_processor import process_video_with_progress
import tempfile
import os

# App title
st.set_page_config(page_title="Video Bounding Box Overlay", layout="centered")
st.title("Video Bounding Box Overlay Tool")

# FIle Uploads
video_file = st.file_uploader("Upload video file", type=["mp4"])
json_file = st.file_uploader("Upload json file", type=["json"])

# Process Button
if video_file and json_file:
    st.success("Files uploaded successfully")

    # Temporary file paths
    temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    temp_json_path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name


    # Save Uploaded file to temp
    with open(temp_video_path, "wb") as f:
        f.write(video_file.read())
    with open(temp_json_path, "wb") as f:
        f.write(json_file.read())

    if st.button("Process Video"):
        st.info("Processing started... Please wait.")

        progress_bar = st.progress(0)
        status_text = st.empty()
        speed_text = st.empty()

        def update_progress(progress, total_frames):
            percent = int((progress/total_frames) * 100)
            progress_bar.progress(percent)
            status_text.write(f"Frames processed: {progress}/{total_frames}")

        try:
            process_video_with_progress(temp_video_path, temp_json_path, output_path, update_progress)
            st.success("Processing completed!")

            # Show the processed video
            st.video(output_path)

            # Provide the download link:
            with open(output_path, "rb") as f:
                st.download_button("Download Processed Video", f, file_name="Processed_video.mp4")
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.warning("Please upload both video and JSON file to process.")
