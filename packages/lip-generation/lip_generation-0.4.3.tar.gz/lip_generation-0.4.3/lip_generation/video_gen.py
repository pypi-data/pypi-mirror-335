from os import listdir, path
import numpy as np
import scipy, cv2, os, sys, argparse
# import .video_generation.audio_mod.audio as audio
from .video_generation.audio_mod import audio as audio
import json, subprocess, random, string
from tqdm import tqdm
from glob import glob
import torch
from .video_generation import Wav2Lip
import time
import cv2



def run_lipsync(checkpoint_path, metadata_path, audio_dir, output_dir='results/', wav2lip_batch_size=128, img_size=96):
    """
    Generate lip-sync videos using Wav2Lip models with preprocessed frames and face data
    Without attaching audio to the final video
    
    Parameters:
    checkpoint_path (str): Path to the saved checkpoint to load weights from
    metadata_path (str): Path to the metadata JSON file with frame paths and bounding boxes
    audio_dir (str): Directory containing audio files to process
    output_dir (str): Directory for output videos
    wav2lip_batch_size (int): Batch size for Wav2Lip model(s)
    img_size (int): Image size for the model
    
    Returns:
    dict: Summary of execution times
    """
    start_time = time.time()
    
    # Handle relative paths by converting to absolute paths
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # checkpoint_path = os.path.abspath(os.path.join(current_dir, checkpoint_path))
    # metadata_path = os.path.abspath(os.path.join(current_dir, metadata_path))
    # audio_dir = os.path.abspath(os.path.join(current_dir, audio_dir))
    # output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
    
    print(f"Using absolute paths:")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Metadata: {metadata_path}")
    print(f"Audio directory: {audio_dir}")
    print(f"Output directory: {output_dir}")
    
    mel_step_size = 16
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('Using {} for inference.'.format(device))
    
    # Create output directories
    os.makedirs('temp', exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    def _load(checkpoint_path):
        if device == 'cuda':
            checkpoint = torch.load(checkpoint_path)
        else:
            checkpoint = torch.load(checkpoint_path,
                                    map_location=lambda storage, loc: storage)
        return checkpoint

    def load_model(path):
        model = Wav2Lip()
        print("Load checkpoint from: {}".format(path))
        checkpoint = _load(path)
        s = checkpoint["state_dict"]
        new_s = {}
        for k, v in s.items():
            new_s[k.replace('module.', '')] = v
        model.load_state_dict(new_s)

        model = model.to(device)
        return model.eval()

    def datagen(frames, mels, face_coords):
        img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []

        for i, m in enumerate(mels):
            idx = i % len(frames)
            frame_to_save = frames[idx].copy()
            
            # Extract face using coordinates
            x1, y1, x2, y2 = face_coords[idx]
            face = frame_to_save[y1:y2, x1:x2].copy()

            face = cv2.resize(face, (img_size, img_size))
                
            img_batch.append(face)
            mel_batch.append(m)
            frame_batch.append(frame_to_save)
            coords_batch.append((y1, y2, x1, x2))

            if len(img_batch) >= wav2lip_batch_size:
                img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)

                img_masked = img_batch.copy()
                img_masked[:, img_size//2:] = 0

                img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
                mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])

                yield img_batch, mel_batch, frame_batch, coords_batch
                img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []

        if len(img_batch) > 0:
            img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)

            img_masked = img_batch.copy()
            img_masked[:, img_size//2:] = 0

            img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
            mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])

            yield img_batch, mel_batch, frame_batch, coords_batch

    def process_audio_file(audio_path, frames, fps, face_coords, model):
        # Create an output path for the temp video (without audio)
        audio_filename = os.path.basename(audio_path).rsplit('.', 1)[0]
        # Save the final video to the output directory
        final_output_path = os.path.join(output_dir, f'{audio_filename}.mp4')
        
        # Time audio preprocessing
        audio_prep_start = time.time()
        if not audio_path.endswith('.wav'):
            print(f'Extracting raw audio from {audio_path}...')
            temp_dir = os.path.join(current_dir, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_wav = os.path.join(temp_dir, f'temp_{audio_filename}.wav')
            command = f'ffmpeg -y -i "{audio_path}" -strict -2 "{temp_wav}"'
            subprocess.call(command, shell=True)
            audio_path = temp_wav

        wav = audio.load_wav(audio_path, 16000)
        mel = audio.melspectrogram(wav)
        audio_prep_time = time.time() - audio_prep_start
        print(f'Audio preprocessing completed in {audio_prep_time:.2f} seconds')
        
        if np.isnan(mel.reshape(-1)).sum() > 0:
            print(f'Warning: Mel contains NaN for {audio_path}. Skipping.')
            return

        # Time mel chunks preparation
        mel_prep_start = time.time()
        mel_chunks = []
        mel_idx_multiplier = 80./fps 
        i = 0
        while 1:
            start_idx = int(i * mel_idx_multiplier)
            if start_idx + mel_step_size > len(mel[0]):
                mel_chunks.append(mel[:, len(mel[0]) - mel_step_size:])
                break
            mel_chunks.append(mel[:, start_idx : start_idx + mel_step_size])
            i += 1
        mel_prep_time = time.time() - mel_prep_start
        print(f'Mel chunks preparation completed in {mel_prep_time:.2f} seconds')

        print(f"Length of mel chunks for {os.path.basename(audio_path)}: {len(mel_chunks)}")
        
        num_frames_needed = len(mel_chunks)
        num_frames_available = len(frames)
        
        print(f"Audio requires {num_frames_needed} frames, video has {num_frames_available} frames")
        
        frame_h, frame_w = frames[0].shape[:-1]
        temp_dir = os.path.join(current_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the temp video with the audio filename instead of a generic name
        temp_video_path = os.path.join(temp_dir, f'{audio_filename}.avi')
        out = cv2.VideoWriter(temp_video_path, 
                             cv2.VideoWriter_fourcc(*'DIVX'), fps, (frame_w, frame_h))

        # Time lip generation
        lip_gen_start = time.time()
        batch_size = wav2lip_batch_size
        gen = datagen(frames.copy(), mel_chunks, face_coords)

        for i, (img_batch, mel_batch, frames_batch, coords) in enumerate(tqdm(gen, 
                                                total=int(np.ceil(float(len(mel_chunks))/batch_size)),
                                                desc=f"Processing {os.path.basename(audio_path)}")):
            img_batch = torch.FloatTensor(np.transpose(img_batch, (0, 3, 1, 2))).to(device)
            mel_batch = torch.FloatTensor(np.transpose(mel_batch, (0, 3, 1, 2))).to(device)

            with torch.no_grad():
                pred = model(mel_batch, img_batch)

            pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.
            
            for p, f, c in zip(pred, frames_batch, coords):
                y1, y2, x1, x2 = c
                p = cv2.resize(p.astype(np.uint8), (x2 - x1, y2 - y1))

                f[y1:y2, x1:x2] = p
                out.write(f)

        out.release()
        lip_gen_time = time.time() - lip_gen_start
        print(f'Lip generation completed in {lip_gen_time:.2f} seconds')
        print("the temp video generated path is", temp_video_path)
        # convert_avi_to_mp4(temp_video_path, final_output_path)
        # Instead of combining with audio, just copy the temp video to the output directory
        # video_creation_start = time.time()
        
        # Just copy the temp video file to the output directory
        # command = f'ffmpeg -y -i "{temp_video_path}" -c:v copy "{final_output_path}"'
        # subprocess.call(command, shell=platform.system() != 'Windows')
        
        # video_creation_time = time.time() - video_creation_start
        # print(f'Video file copied to output directory in {video_creation_time:.2f} seconds')
        
        # Don't remove the temp file as that's what we want to keep
        # print(f'Temporary video file saved at: {temp_video_path}')
        # print(f'Final video file (without audio) saved at: {final_output_path}')
        video_creation_time = 0
        return {
            'audio_prep_time': audio_prep_time,
            'mel_prep_time': mel_prep_time,
            'lip_gen_time': lip_gen_time,
            # 'video_creation_time': video_creation_time,
            'total_time': audio_prep_time + mel_prep_time + lip_gen_time + video_creation_time,
            'temp_video_path': temp_video_path,
            'final_output_path': final_output_path
        }

    # Load metadata
    print(f"Loading metadata from {metadata_path}")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    fps = metadata['fps']
    print(f"Video FPS: {fps}")
    
    # Load all frames
    print("Loading frames...")
    frames = []
    face_coords = []
    
    for frame_data in tqdm(metadata['frames'], desc="Loading frames"):
        frame_path = frame_data['frame_path']
        # print(frame_path)
        new_path = frame_path.replace("output\\", "")
        # print(new_path)
        # Convert relative frame path to absolute if needed
        if not os.path.isabs(new_path):
            # Get directory of metadata file to use as base for relative frame paths
            metadata_dir = os.path.dirname(metadata_path)
            new_path = os.path.abspath(os.path.join((metadata_dir), new_path))
        
        bbox = frame_data['bbox']
        
        frame = cv2.imread(new_path)
        if frame is None:
            raise ValueError(f"Could not load frame: {new_path}")
        
        frames.append(frame)
        face_coords.append(bbox)
    
    print(f"Loaded {len(frames)} frames")
    
    # Time model loading
    model_loading_start = time.time()
    model = load_model(checkpoint_path)
    model_loading_time = time.time() - model_loading_start
    print(f'Model loading completed in {model_loading_time:.2f} seconds')
    
    # Process audio files
    if os.path.isdir(audio_dir):
        audio_files = []
        for ext in ['wav', 'mp3', 'm4a', 'aac', 'flac']:
            audio_files.extend(glob(os.path.join(audio_dir, f'*.{ext}')))
        
        if not audio_files:
            raise ValueError(f"No audio files found in {audio_dir}")
        
        print(f"Found {len(audio_files)} audio files to process")
        video_generation_start = time.time()
        
        audio_processing_results = []
        for audio_file in audio_files:
            each_audio_start = time.time() 
            print(f"\nProcessing {os.path.basename(audio_file)}...")
            result = process_audio_file(audio_file, frames, fps, face_coords, model)
            if result:
                audio_processing_results.append({
                    'audio_file': audio_file,
                    'processing_time': time.time() - each_audio_start,
                    'details': result
                })
            print(f"Audio file {os.path.basename(audio_file)} processed in {time.time() - each_audio_start:.2f} seconds")
        
        video_generation_time = time.time() - video_generation_start
        print(f"Total video generation time: {video_generation_time:.2f} seconds")
            
    else:
        raise ValueError('audio_dir must be a valid directory containing audio files')
    
    total_time = time.time() - start_time
    execution_summary = {
        'model_loading_time': model_loading_time,
        'video_generation_time': video_generation_time,
        'total_execution_time': total_time,
        'audio_processing_results': audio_processing_results
    }
    
    print(f"\nTotal execution summary:")
    print(f"Model loading time: {model_loading_time:.2f}s")
    print(f"Video generation time: {video_generation_time:.2f}s")
    print(f"Total execution time: {total_time:.2f}s")
    
    return execution_summary



# Example of how to use this function directly in another script:
# if __name__ == '__main__':

#     run_lipsync(
#         checkpoint_path="checkpoints/wav2lip.pth",
#         metadata_path="../output/metadata.json",
#         audio_dir= "../input_audio/",
#         output_dir="../output_videos/",
#     )