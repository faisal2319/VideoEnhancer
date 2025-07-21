import cv2
import os
import logging
import subprocess
import numpy as np
import shutil
from datetime import datetime
from video_frame_extraction import extract_frames
from enhancer import enhance_image
from analyzer import analyze_video

logger = logging.getLogger(__name__)

def create_comparison_video(video_path="input.mp4", output_path="ml_output/comparison.mp4"):
    """Create a side-by-side comparison video showing original vs enhanced frames"""
    logger.info("=" * 60)
    logger.info("CREATING SIDE-BY-SIDE COMPARISON VIDEO")
    logger.info("=" * 60)
    logger.info(f"Input video: {video_path}")
    logger.info(f"Output video: {output_path}")
    
    # Create output directories
    os.makedirs("ml_output/frames", exist_ok=True)
    os.makedirs("ml_output/enhanced", exist_ok=True)
    os.makedirs("ml_output/comparison_frames", exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Step 1: Extract ALL frames from video
    logger.info("-" * 40)
    logger.info("STEP 1: EXTRACTING ALL FRAMES")
    logger.info("-" * 40)
    try:
        total_frames = extract_frames(video_path, "ml_output/frames", extract_all_frames=True)
        logger.info(f"Extracted {total_frames} frames")
    except Exception as e:
        logger.error(f"Frame extraction failed: {str(e)}")
        raise
    
    # Step 2: Analyze video quality
    logger.info("-" * 40)
    logger.info("STEP 2: ANALYZING VIDEO QUALITY")
    logger.info("-" * 40)
    try:
        results = analyze_video("ml_output/frames")
        logger.info(f"Analyzed {len(results)} frames")
        
        blurry_count = sum(1 for r in results if r["blurry"])
        dark_count = sum(1 for r in results if r["dark"])
        good_count = len(results) - blurry_count - dark_count
        logger.info(f"Analysis: {blurry_count} blurry, {dark_count} dark, {good_count} good")
    except Exception as e:
        logger.error(f"Video analysis failed: {str(e)}")
        raise
    
    # Step 3: Process frames and create comparison frames
    logger.info("-" * 40)
    logger.info("STEP 3: CREATING COMPARISON FRAMES")
    logger.info("-" * 40)
    
    enhanced_count = 0
    copied_count = 0
    
    try:
        for i, result in enumerate(results):
            original_path = os.path.join("ml_output/frames", result["filename"])
            enhanced_path = os.path.join("ml_output/enhanced", result["filename"])
            comparison_path = os.path.join("ml_output/comparison_frames", result["filename"])
            
            # Read original frame
            original_frame = cv2.imread(original_path)
            if original_frame is None:
                logger.warning(f"Failed to read original frame: {original_path}")
                continue
            
            # Process frame (enhance if needed, copy if good)
            if result["blurry"] or result["dark"]:
                logger.info(f"Enhancing frame {i+1}/{len(results)}: {result['filename']} "
                          f"(blurry: {result['blurry']}, dark: {result['dark']})")
                enhance_image(original_path, enhanced_path)
                enhanced_frame = cv2.imread(enhanced_path)
                
                # Ensure enhanced frame has same dimensions as original
                if enhanced_frame is not None and enhanced_frame.shape[:2] != original_frame.shape[:2]:
                    logger.warning(f"Enhanced frame has different dimensions, resizing to match original")
                    enhanced_frame = cv2.resize(enhanced_frame, (original_frame.shape[1], original_frame.shape[0]))
                    cv2.imwrite(enhanced_path, enhanced_frame)
                
                enhanced_count += 1
            else:
                logger.debug(f"Copying frame {i+1}/{len(results)}: {result['filename']} (no enhancement needed)")
                shutil.copy(original_path, enhanced_path)
                enhanced_frame = cv2.imread(enhanced_path)
                copied_count += 1
            
            if enhanced_frame is None:
                logger.warning(f"Failed to read enhanced frame: {enhanced_path}")
                continue
            
            # Create side-by-side comparison frame
            comparison_frame = create_side_by_side_frame(original_frame, enhanced_frame, result)
            cv2.imwrite(comparison_path, comparison_frame)
            
            # Progress update
            if (i + 1) % 50 == 0:
                progress = ((i + 1) / len(results)) * 100
                logger.info(f"Progress: {progress:.1f}% ({i+1}/{len(results)} frames)")
        
        logger.info(f"Frame processing completed: {enhanced_count} enhanced, {copied_count} copied")
    except Exception as e:
        logger.error(f"Frame processing failed: {str(e)}")
        raise
    
    # Step 4: Create comparison video with audio
    logger.info("-" * 40)
    logger.info("STEP 4: CREATING COMPARISON VIDEO")
    logger.info("-" * 40)
    try:
        # Get original video properties for correct FPS
        cap = cv2.VideoCapture(video_path)
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        logger.info(f"Original video FPS: {original_fps}")
        
        # Create video from comparison frames
        temp_video_path = output_path.replace('.mp4', '_temp.mp4')
        
        # Get dimensions from first comparison frame and ensure consistency
        first_frame_path = os.path.join("ml_output/comparison_frames", sorted(os.listdir("ml_output/comparison_frames"))[0])
        first_frame = cv2.imread(first_frame_path)
        height, width, channels = first_frame.shape
        
        logger.info(f"Comparison video dimensions: {width}x{height}")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(temp_video_path, fourcc, original_fps, (width, height))
        
        if not writer.isOpened():
            raise ValueError(f"Failed to initialize video writer for: {temp_video_path}")
        
        # Process comparison frames
        comparison_frames = sorted([f for f in os.listdir("ml_output/comparison_frames") if f.endswith(".jpg")])
        logger.info(f"Creating video from {len(comparison_frames)} comparison frames")
        
        for i, frame_file in enumerate(comparison_frames):
            frame_path = os.path.join("ml_output/comparison_frames", frame_file)
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                # Ensure frame has the correct dimensions
                if frame.shape[:2] != (height, width):
                    logger.warning(f"Frame {frame_file} has wrong dimensions {frame.shape[:2]}, resizing to {width}x{height}")
                    frame = cv2.resize(frame, (width, height))
                
                writer.write(frame)
            else:
                logger.error(f"Failed to read frame: {frame_path}")
            
            if (i + 1) % 50 == 0:
                progress = ((i + 1) / len(comparison_frames)) * 100
                logger.info(f"Video creation progress: {progress:.1f}% ({i+1}/{len(comparison_frames)} frames)")
        
        writer.release()
        logger.info("Temporary video created successfully")
        
        # Add audio from original video
        logger.info("Adding audio from original video...")
        try:
            cmd = [
                'ffmpeg', '-i', temp_video_path,  # Video input
                '-i', video_path,                  # Audio input
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
                logger.info("Audio successfully added to comparison video!")
                os.remove(temp_video_path)
                logger.info(f"Temporary file removed: {temp_video_path}")
            else:
                logger.warning(f"Failed to add audio: {result.stderr}")
                logger.info("Using video without audio...")
                os.rename(temp_video_path, output_path)
                
        except Exception as e:
            logger.warning(f"Error adding audio: {str(e)}")
            logger.info("Using video without audio...")
            os.rename(temp_video_path, output_path)
        
        logger.info(f"Comparison video created successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Video creation failed: {str(e)}")
        raise
    
    # Final summary
    logger.info("=" * 60)
    logger.info("COMPARISON VIDEO CREATION COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Output: {output_path}")
    logger.info(f"Summary: {len(results)} total frames, {enhanced_count} enhanced, {copied_count} copied")
    
    return output_path

def create_side_by_side_frame(original_frame, enhanced_frame, analysis_result):
    """Create a side-by-side comparison frame with labels and indicators"""
    # Ensure both frames have the same dimensions
    h1, w1 = original_frame.shape[:2]
    h2, w2 = enhanced_frame.shape[:2]
    
    # Use the larger height to accommodate both frames
    target_height = max(h1, h2)
    target_width = w1 + w2 + 50  # Extra space for separation and labels
    
    # Create canvas with fixed dimensions
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    canvas.fill(255)  # White background
    
    # Resize frames to fit - ensure consistent dimensions
    original_resized = cv2.resize(original_frame, (w1, target_height))
    enhanced_resized = cv2.resize(enhanced_frame, (w2, target_height))
    
    # Place frames side by side
    canvas[:, :w1] = original_resized
    canvas[:, w1+50:w1+50+w2] = enhanced_resized
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 2
    color = (0, 0, 0)  # Black text
    
    # Original label
    cv2.putText(canvas, "ORIGINAL", (10, 30), font, font_scale, color, thickness)
    
    # Enhanced label
    cv2.putText(canvas, "ENHANCED", (w1 + 60, 30), font, font_scale, color, thickness)
    
    # Add enhancement indicators
    if analysis_result["blurry"] or analysis_result["dark"]:
        indicator_color = (0, 255, 0)  # Green for enhanced
        indicator_text = "ENHANCED"
        if analysis_result["blurry"]:
            indicator_text += " (Blurry)"
        if analysis_result["dark"]:
            indicator_text += " (Dark)"
    else:
        indicator_color = (128, 128, 128)  # Gray for no enhancement
        indicator_text = "NO CHANGE"
    
    # Add indicator text
    cv2.putText(canvas, indicator_text, (w1 + 60, target_height - 20), 
                font, 0.7, indicator_color, thickness)
    
    # Add separator line
    cv2.line(canvas, (w1 + 25, 0), (w1 + 25, target_height), (0, 0, 0), 2)
    
    return canvas

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    create_comparison_video() 