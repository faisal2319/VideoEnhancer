import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "Real-ESRGAN"))
import logging
import cv2
import numpy as np
import torch
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from quality_check import is_low_resolution, is_pixelated

logger = logging.getLogger(__name__)

def enhance_image(image_path, output_path):
    """Enhance image using RealESRGAN if low-res or pixelated; otherwise, just copy input to output."""
    logger.info(f"Starting image enhancement: {image_path} -> {output_path}")
    
    try:
        # Load image
        logger.info(f"Loading image: {image_path}")
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
        logger.info(f"Image loaded - Shape: {img.shape}")

        # Check if enhancement is needed
        low_res = is_low_resolution(img)
        pixelated = is_pixelated(img)
        logger.info(f"Low-resolution: {low_res}, Pixelated: {pixelated}")
        if not (low_res or pixelated):
            logger.info("Image is not low-resolution or pixelated. Skipping enhancement. Copying input to output.")
            success = cv2.imwrite(output_path, img)
            if not success:
                logger.error("Failed to save image (copy mode)")
                raise RuntimeError("Failed to save image (copy mode)")
            return False  # Enhancement not performed

        # Load and setup model
        logger.info("Initializing RealESRGAN model...")
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        # Create the model architecture
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        
        # Initialize the RealESRGANer with proper settings
        upsampler = RealESRGANer(
            scale=4,
            model_path="Real-ESRGAN/weights/RealESRGAN_x2plus.pth",
            model=model,
            tile=0,  # No tiling to prevent grid
            tile_pad=0,  # No padding
            pre_pad=0,  # No pre-padding
            half=False,  # Use full precision
            device=device
        )
        logger.info("RealESRGAN model initialized successfully")
        
        # Perform enhancement using the official enhance method
        logger.info("Starting image enhancement...")
        
        with torch.no_grad():
            output, _ = upsampler.enhance(img)
            output = np.clip(output, 0, 255).astype(np.uint8)
        
        logger.info(f"Enhancement completed - Output shape: {output.shape}")
        
        # Save enhanced image
        logger.info(f"Saving enhanced image to: {output_path}")
        success = cv2.imwrite(output_path, output)
        if success:
            logger.info("Enhanced image saved successfully")
        else:
            logger.error("Failed to save enhanced image")
            raise RuntimeError("Failed to save enhanced image")
        
        return True  # Enhancement performed
        
    except Exception as e:
        logger.error(f"Image enhancement failed: {str(e)}")
        raise

