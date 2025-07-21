import os 
import cv2
import logging
from quality_check import get_quality_score
from typing import Dict, Any

logger = logging.getLogger(__name__)

def analyze_video(frame_dir):
    """Analyze video quality with detailed logging"""
    logger.info(f"Starting video quality analysis for directory: {frame_dir}")
    
    try:
        # Check if directory exists
        if not os.path.exists(frame_dir):
            error_msg = f"Frame directory does not exist: {frame_dir}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Get list of frame files
        logger.info("Scanning for frame files...")
        frame_files = [f for f in sorted(os.listdir(frame_dir)) if f.endswith(".jpg")]
        
        if not frame_files:
            error_msg = f"No frame files found in directory: {frame_dir}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Found {len(frame_files)} frame files to analyze")
        
        # Analyze each frame
        logger.info("Starting frame quality analysis...")
        results = []
        
        for i, file in enumerate(frame_files):
            frame_path = os.path.join(frame_dir, file)
            logger.debug(f"Analyzing frame {i+1}/{len(frame_files)}: {file}")
            
            try:
                img = cv2.imread(frame_path)
                
                if img is None:
                    logger.warning(f"Failed to read frame: {frame_path}")
                    continue
                
                # Get quality score
                quality_score: Dict[str, Any] = get_quality_score(img)
                quality_score["filename"] = file
                results.append(quality_score)
                
                # Log progress every 10 frames
                if (i + 1) % 10 == 0:
                    progress = ((i + 1) / len(frame_files)) * 100
                    logger.info(f"Analysis progress: {progress:.1f}% ({i+1}/{len(frame_files)} frames)")
                
            except Exception as e:
                logger.error(f"Error analyzing frame {file}: {str(e)}")
                continue
        
        # Log analysis summary
        logger.info("Video analysis completed successfully!")
        logger.info(f"Successfully analyzed {len(results)} frames")
        
        if results:
            blurry_count = sum(1 for r in results if r["blurry"])
            dark_count = sum(1 for r in results if r["dark"])
            low_res_count = sum(1 for r in results if r.get("low_resolution"))
            pixelated_count = sum(1 for r in results if r.get("pixelated"))
            # A frame is 'good' if it is not blurry, not dark, not low-res, and not pixelated
            good_count = len(results) - blurry_count - dark_count - low_res_count - pixelated_count
            
            logger.info(f"Analysis summary:")
            logger.info(f"  - Total frames: {len(results)}")
            logger.info(f"  - Blurry frames: {blurry_count}")
            logger.info(f"  - Dark frames: {dark_count}")
            logger.info(f"  - Low-resolution frames: {low_res_count}")
            logger.info(f"  - Pixelated frames: {pixelated_count}")
            logger.info(f"  - Good frames: {good_count}")
        
        return results
        
    except Exception as e:
        logger.error(f"Video analysis failed: {str(e)}")
        raise