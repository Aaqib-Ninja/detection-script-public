# video_processor.py

import cv2
import json
from datetime import datetime
from tqdm import tqdm


def parse_jsonl_file(path):
    with open(path, 'r') as f:
        for line in f:
            yield json.loads(line)


def extract_start_timestamp(jsonl_path):
    for entry in parse_jsonl_file(jsonl_path):
        return datetime.fromisoformat(entry['timestamp'].replace("Z", "+00:00"))
    raise ValueError("No entries found in JSONL file.")


def convert_timestamp_to_frame(timestamp_str, video_start_time, fps):
    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    delta = (dt - video_start_time).total_seconds()
    return int(delta * fps)


def draw_bounding_boxes(frame, boxes_with_ids, frame_width, frame_height):
    for box, person_id in boxes_with_ids:
        x0 = int(box['x0'] * frame_width)
        y0 = int(box['y0'] * frame_height)
        x1 = int(box['x1'] * frame_width)
        y1 = int(box['y1'] * frame_height)

        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
        label = str(person_id)
        label_y = y0 - 10 if y0 - 10 > 10 else y0 + 10
        cv2.putText(
            frame, label, (x0, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2
        )
    return frame


def process_video(video_path, jsonl_path, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"[INFO] FPS: {fps}, Resolution: {width}x{height}, Total frames: {total_frames}")

    video_start_time = extract_start_timestamp(jsonl_path)
    frame_map = {}

    for entry in parse_jsonl_file(jsonl_path):
        tz_to_frame = convert_timestamp_to_frame(entry['timestamp'], video_start_time, fps)
        for person_id, box in entry['boundingBoxes'].items():
            for i in range(tz_to_frame, tz_to_frame + 3):
                frame_map.setdefault(i, []).append((box, person_id))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print("[INFO] Starting video processing...")
    for frame_id in tqdm(range(total_frames)):
        ret, frame = cap.read()
        if not ret:
            break

        boxes = frame_map.get(frame_id, [])
        if boxes:
            frame = draw_bounding_boxes(frame, boxes, width, height)

        out.write(frame)

    cap.release()
    out.release()
    print("[INFO] Finished writing output video:", output_path)


# Add this version of process_video_with_progress in video_processor.py

def process_video_with_progress(video_path, jsonl_path, output_path, progress_callback):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"[INFO] FPS: {fps}, Resolution: {width}x{height}, Total frames: {total_frames}")

    video_start_time = extract_start_timestamp(jsonl_path)
    frame_map = {}

    for entry in parse_jsonl_file(jsonl_path):
        tz_to_frame = convert_timestamp_to_frame(entry['timestamp'], video_start_time, fps)
        for person_id, box in entry['boundingBoxes'].items():
            for i in range(tz_to_frame, tz_to_frame + 3):
                frame_map.setdefault(i, []).append((box, person_id))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print("[INFO] Starting video processing...")
    for frame_id in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        boxes = frame_map.get(frame_id, [])
        if boxes:
            frame = draw_bounding_boxes(frame, boxes, width, height)

        out.write(frame)
        progress_callback(frame_id + 1, total_frames)

    cap.release()
    out.release()
    print("[INFO] Finished writing output video:", output_path)
