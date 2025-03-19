from os import listdir, path
import numpy as np
import cv2
import os
import json
from tqdm import tqdm
import torch
from .face_detection import face_alignment as face_detect_w
import time
from pathlib import Path

def extract_faces(
    face_path,
    output_dir,
    static=False,
    fps=25.0,
    pads=[0, 10, 0, 0],
    face_det_batch_size=16,
    resize_factor=2,
    crop=[0, -1, 0, -1],
    box=[-1, -1, -1, -1],
    rotate=False,
    nosmooth=False
):
    """
    Extract frames and face bounding boxes from video for Wav2Lip
    
    Parameters:
    face_path (str): Filepath of video/image that contains faces to use
    output_dir (str): Directory to save frames and face data
    static (bool): If True, then use only first video frame for inference
    fps (float): Can be specified only if input is a static image
    pads (list): Padding (top, bottom, left, right). Please adjust to include chin at least
    face_det_batch_size (int): Batch size for face detection
    resize_factor (int): Reduce the resolution by this factor
    crop (list): Crop video to a smaller region (top, bottom, left, right)
    box (list): Specify a constant bounding box for the face
    rotate (bool): If true, will flip video right by 90deg
    nosmooth (bool): Prevent smoothing face detections over a short temporal window
    
    Returns:
    dict: Metadata about the processed frames and face boxes
    """
    start_time = time.time()
    print("batch size is ", face_det_batch_size)
    img_size = 96
    # face_path = os.path.normpath(face_path)
    print(face_path)
    if not os.path.isfile(face_path):
        raise ValueError('face_path argument must be a valid path to video/image file')
    
    if os.path.isfile(face_path) and face_path.split('.')[1] in ['jpg', 'png', 'jpeg']:
        static = True
    
    # Create output directories
    frames_dir = os.path.join(output_dir, 'frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    
    # Time video frame reading and saving
    print('Reading and saving video frames...')
    full_frames = []
    frame_paths = []
    
    if face_path.split('.')[1] in ['jpg', 'png', 'jpeg']:
        frame = cv2.imread(face_path)
        
        # Apply resize and crop if needed
        if resize_factor > 1:
            frame = cv2.resize(frame, (frame.shape[1]//resize_factor, frame.shape[0]//resize_factor))
        
        if rotate:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        y1, y2, x1, x2 = crop
        if x2 == -1: x2 = frame.shape[1]
        if y2 == -1: y2 = frame.shape[0]
        
        frame = frame[y1:y2, x1:x2]
        full_frames.append(frame)
        
        # Save the frame
        frame_path = os.path.join(frames_dir, f"frame_0.jpg")
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)
        
    else:
        video_stream = cv2.VideoCapture(face_path)
        fps = video_stream.get(cv2.CAP_PROP_FPS)
        
        frame_idx = 0
        while True:
            still_reading, frame = video_stream.read()
            if not still_reading:
                video_stream.release()
                break
                
            if resize_factor > 1:
                frame = cv2.resize(frame, (frame.shape[1]//resize_factor, frame.shape[0]//resize_factor))
            
            if rotate:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            
            y1, y2, x1, x2 = crop
            if x2 == -1: x2 = frame.shape[1]
            if y2 == -1: y2 = frame.shape[0]
            
            frame = frame[y1:y2, x1:x2]
            full_frames.append(frame)
            
            # Save the frame
            frame_path = os.path.join(frames_dir, f"frame_{frame_idx}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            frame_idx += 1
    
    print(f"Total frames extracted and saved: {len(full_frames)}")
    
    # Helper functions
    def get_smoothened_boxes(boxes, T):
        for i in range(len(boxes)):
            if i + T > len(boxes):
                window = boxes[len(boxes) - T:]
            else:
                window = boxes[i : i + T]
            boxes[i] = np.mean(window, axis=0)
        return boxes

    def face_detect(images):
        start_time = time.time()
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        detector = face_detect_w.FaceAlignment(face_detect_w.LandmarksType._2D, 
                                                flip_input=False, device=device)

        batch_size = face_det_batch_size
        print("batch size(2)", face_det_batch_size)
        
        while 1:
            predictions = []
            try:
                for i in tqdm(range(0, len(images), batch_size), desc="Face detection"):
                    predictions.extend(detector.get_detections_for_batch(np.array(images[i:i + batch_size])))
            except RuntimeError as e:
                print(batch_size)
                print(e)
                # if batch_size == 1: 
                #     raise RuntimeError('Image too big to run face detection on GPU. Please use the resize_factor parameter')
                if batch_size != 1:
                    batch_size //= 2
                    print('Recovering from OOM error; New batch size: {}'.format(batch_size))
                    continue
            break

        results = []
        pady1, pady2, padx1, padx2 = pads
        for rect, image in zip(predictions, images):
            if rect is None:
                cv2.imwrite(os.path.join(output_dir, 'faulty_frame.jpg'), image)
                raise ValueError('Face not detected! Ensure the video contains a face in all the frames.')

            y1 = max(0, rect[1] - pady1)
            y2 = min(image.shape[0], rect[3] + pady2)
            x1 = max(0, rect[0] - padx1)
            x2 = min(image.shape[1], rect[2] + padx2)
            
            results.append([x1, y1, x2, y2])

        boxes = np.array(results)
        if not nosmooth: 
            boxes = get_smoothened_boxes(boxes, T=5)
        
        face_detect_time = time.time() - start_time
        print(f'Face detection completed in {face_detect_time:.2f} seconds')
        
        return boxes
    
    # Detect faces or use specified box
    if box[0] == -1:
        print("Running face detection...")
        if static:
            face_boxes = face_detect([full_frames[0]])
            # Replicate the same box for all frames
            face_boxes = np.tile(face_boxes, (len(full_frames), 1))
        else:
            face_boxes = face_detect(full_frames)
    else:
        print('Using the specified bounding box instead of face detection...')
        y1, y2, x1, x2 = box
        # Create bounding boxes for all frames using the specified coordinates
        face_boxes = np.array([[x1, y1, x2, y2]] * len(full_frames))
    
    # Save face bounding box data with corresponding frame paths
    data = {
        'fps': fps,
        'frames': []
    }
    
    for i, (frame_path, box) in enumerate(zip(frame_paths, face_boxes)):
        data['frames'].append({
            'frame_path': frame_path,
            'bbox': box.tolist()  # [x1, y1, x2, y2]
        })
    
    # Save metadata to JSON file
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Metadata saved to: {metadata_path}")
    print(f"Frames saved to: {frames_dir}")
    
    total_time = time.time() - start_time
    print(f"Total execution time: {total_time:.2f} seconds")
    
    return data

# Example usage
# if __name__ == '__main__':
#     # Example of how to call the function
#     result = extract_faces(
#         face_path= "../inputs/video.mp4",
#         output_dir='output',
#         resize_factor=2,
#         pads=[0, 10, 0, 0],
#     )