import cv2
import os
import logging
import subprocess

logger = logging.getLogger(__name__)

def reconstruct_video(frame_dir, output_path, original_video_path=None, fps=24):
    """Reconstruct video from frames with audio preservation"""
    logger.info(f"Starting video reconstruction from: {frame_dir}")
    logger.info(f"Output video path: {output_path}")
    logger.info(f"Original video path: {original_video_path}")
    logger.info(f"Target FPS: {fps}")
    
    try:
        # Get sorted list of frame files
        logger.info("Scanning for frame files...")
        frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
        
        if not frames:
            error_msg = f"No frame files found in directory: {frame_dir}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Found {len(frames)} frame files")
        
        # Get video dimensions from first frame
        logger.info("Reading first frame to determine video dimensions...")
        first_frame_path = os.path.join(frame_dir, frames[0])
        first_frame = cv2.imread(first_frame_path)
        
        if first_frame is None:
            error_msg = f"Failed to read first frame: {first_frame_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        height, width, channels = first_frame.shape
        logger.info(f"Video dimensions: {width}x{height}, Channels: {channels}")
        
        # Create temporary video without audio
        temp_video_path = output_path.replace('.mp4', '_temp.mp4')
        logger.info(f"Creating temporary video: {temp_video_path}")
        
        # Initialize video writer
        logger.info("Initializing video writer...")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            error_msg = f"Failed to initialize video writer for: {temp_video_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Video writer initialized successfully")
        
        # Process frames
        logger.info("Starting frame processing...")
        processed_frames = 0
        
        for i, frame_file in enumerate(frames):
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            
            if frame is None:
                logger.warning(f"Failed to read frame: {frame_path}")
                continue
            
            writer.write(frame)
            processed_frames += 1
            
            # Progress update every 50 frames
            if processed_frames % 50 == 0:
                progress = (processed_frames / len(frames)) * 100
                logger.info(f"Processing progress: {progress:.1f}% ({processed_frames}/{len(frames)} frames)")
        
        # Release video writer
        writer.release()
        logger.info("Video writer released")
        
        logger.info(f"Temporary video created successfully!")
        logger.info(f"Total frames processed: {processed_frames}")
        
        # If we have the original video, add audio back
        if original_video_path and os.path.exists(original_video_path):
            logger.info("Adding audio from original video...")
            try:
                # Use ffmpeg to combine video with original audio
                cmd = [
                    'ffmpeg', '-i', temp_video_path,  # Video input
                    '-i', original_video_path,         # Audio input
                    '-c:v', 'copy',                    # Copy video codec
                    '-c:a', 'aac',                     # Use AAC for audio
                    '-map', '0:v:0',                   # Use video from first input
                    '-map', '1:a:0',                   # Use audio from second input
                    output_path,                       # Output file
                    '-y'                               # Overwrite output
                ]
                
                logger.info(f"Running command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("Audio successfully added to video!")
                    # Clean up temporary file
                    os.remove(temp_video_path)
                    logger.info(f"Temporary file removed: {temp_video_path}")
                else:
                    logger.warning(f"Failed to add audio: {result.stderr}")
                    logger.info("Using video without audio...")
                    # If audio addition fails, just rename the temp file
                    os.rename(temp_video_path, output_path)
                    
            except Exception as e:
                logger.warning(f"Error adding audio: {str(e)}")
                logger.info("Using video without audio...")
                # If audio addition fails, just rename the temp file
                os.rename(temp_video_path, output_path)
        else:
            logger.info("No original video provided, using video without audio...")
            os.rename(temp_video_path, output_path)
        
        logger.info(f"Video reconstruction completed successfully!")
        logger.info(f"Output video: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Video reconstruction failed: {str(e)}")
        raise

