import cv2
import os
import logging
import subprocess

logger = logging.getLogger(__name__)

def extract_frames(video_path, output_dir, extract_all_frames=True):
    """Extract frames from video with detailed logging"""
    logger.info(f"Starting frame extraction from: {video_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Extract all frames: {extract_all_frames}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory created/verified: {output_dir}")
    
    # Open video capture
    logger.info("Opening video capture...")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        error_msg = f"Failed to open video file: {video_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0
    
    logger.info(f"Video properties - FPS: {video_fps:.2f}, Total frames: {total_frames}, Duration: {duration:.2f}s")
    
    # Extract frames
    logger.info("Starting frame extraction...")
    saved_frames = 0
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logger.info("Reached end of video")
                break
                
            # Save every frame if extract_all_frames is True, otherwise sample
            if extract_all_frames:
                frame_path = os.path.join(output_dir, f"frame_{saved_frames:06d}.jpg")
                success = cv2.imwrite(frame_path, frame)
                
                if success:
                    saved_frames += 1
                    if saved_frames % 100 == 0:  # Log every 100th frame
                        logger.info(f"Extracted {saved_frames} frames so far...")
                else:
                    logger.error(f"Failed to save frame {saved_frames} to {frame_path}")
            else:
                # Original logic for sampling frames
                frame_interval = int(video_fps // 1) if video_fps > 0 else 1
                if saved_frames % frame_interval == 0:
                    frame_path = os.path.join(output_dir, f"frame_{saved_frames:06d}.jpg")
                    success = cv2.imwrite(frame_path, frame)
                    
                    if success:
                        saved_frames += 1
                        if saved_frames % 10 == 0:
                            logger.info(f"Extracted {saved_frames} frames so far...")
                    else:
                        logger.error(f"Failed to save frame {saved_frames} to {frame_path}")
                saved_frames += 1
    
    except Exception as e:
        logger.error(f"Error during frame extraction: {str(e)}")
        raise
    finally:
        cap.release()
        logger.info("Video capture released")
    
    logger.info(f"Frame extraction completed successfully!")
    logger.info(f"Total frames saved: {saved_frames}")
    logger.info(f"Output directory: {output_dir}")
    
    return saved_frames

def extract_audio(video_path, output_audio_path):
    """Extract audio from video using ffmpeg"""
    logger.info(f"Extracting audio from: {video_path}")
    logger.info(f"Output audio path: {output_audio_path}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        
        # Use ffmpeg to extract audio
        cmd = [
            'ffmpeg', '-i', video_path, 
            '-vn', '-acodec', 'copy',  # No video, copy audio codec
            output_audio_path,
            '-y'  # Overwrite output file
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Audio extraction completed successfully!")
            return output_audio_path
        else:
            error_msg = f"Audio extraction failed: {result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
    except Exception as e:
        logger.error(f"Audio extraction failed: {str(e)}")
        raise