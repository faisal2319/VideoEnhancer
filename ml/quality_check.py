import cv2
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def is_blurry(image, threshold=100):  # Lowered from 100 to 50
    """Check if image is blurry with detailed logging"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        is_blurry_result = lap_var < threshold
        
        logger.debug(f"Blur analysis - Laplacian variance: {lap_var:.2f}, Threshold: {threshold}, Is blurry: {is_blurry_result}")
        
        return is_blurry_result
        
    except Exception as e:
        logger.error(f"Error in blur detection: {str(e)}")
        return False

def is_dark(image, threshold=100):  # Lowered from 100 to 80
    """Check if image is dark with detailed logging"""
    try:
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate average brightness from V channel
        brightness = hsv[..., 2].mean()
        
        is_dark_result = brightness < threshold
        
        logger.debug(f"Brightness analysis - Average brightness: {brightness:.2f}, Threshold: {threshold}, Is dark: {is_dark_result}")
        
        return is_dark_result
        
    except Exception as e:
        logger.error(f"Error in brightness detection: {str(e)}")
        return False

def is_low_resolution(image, min_width=1280, min_height=720):
    """Check if image is low-resolution (default: below 1280x720)"""
    try:
        height, width = image.shape[:2]
        is_low_res = width < min_width or height < min_height
        logger.debug(f"Resolution analysis - Size: {width}x{height}, Min: {min_width}x{min_height}, Is low-res: {is_low_res}")
        return is_low_res
    except Exception as e:
        logger.error(f"Error in resolution detection: {str(e)}")
        return False

def is_pixelated(image, block_size=8, threshold=15):
    """Check if image is pixelated using blockiness metric (mean absolute diff between blocks)"""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        blockiness = 0
        count = 0
        # Horizontal block edges
        for y in range(block_size, h, block_size):
            diff = np.abs(gray[y, :] - gray[y-1, :]).mean()
            blockiness += diff
            count += 1
        # Vertical block edges
        for x in range(block_size, w, block_size):
            diff = np.abs(gray[:, x] - gray[:, x-1]).mean()
            blockiness += diff
            count += 1
        avg_blockiness = blockiness / max(count, 1)
        is_pixelated_result = avg_blockiness > threshold
        logger.debug(f"Pixelation analysis - Avg blockiness: {avg_blockiness:.2f}, Threshold: {threshold}, Is pixelated: {is_pixelated_result}")
        return is_pixelated_result
    except Exception as e:
        logger.error(f"Error in pixelation detection: {str(e)}")
        return False

def get_quality_score(image):
    """Get comprehensive quality score with detailed logging"""
    logger.debug("Starting quality analysis...")
    
    try:
        # Get image properties
        height, width, channels = image.shape
        logger.debug(f"Image properties - Size: {width}x{height}, Channels: {channels}")
        
        # Perform quality checks
        blurry = is_blurry(image)
        dark = is_dark(image)
        low_res = is_low_resolution(image)
        pixelated = is_pixelated(image)
        
        # Create quality score dictionary
        quality_score: Dict[str, Any] = {
            "blurry": blurry,
            "dark": dark,
            "low_resolution": low_res,
            "pixelated": pixelated,
        }
        
        logger.debug(f"Quality analysis completed - Blurry: {blurry}, Dark: {dark}, Low-res: {low_res}, Pixelated: {pixelated}")
        
        return quality_score
        
    except Exception as e:
        logger.error(f"Error in quality analysis: {str(e)}")
        # Return default values on error
        return {
            "blurry": False,
            "dark": False,
            "low_resolution": False,
            "pixelated": False,
        }
