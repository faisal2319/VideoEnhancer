import cv2
import os
import logging

logger = logging.getLogger(__name__)

def debug_comparison_video():
    """Debug the comparison video to find why it goes black"""
    logger.info("Debugging comparison video...")
    
    # Check comparison frames
    comparison_dir = "ml_output/comparison_frames"
    frames = sorted([f for f in os.listdir(comparison_dir) if f.endswith(".jpg")])
    
    logger.info(f"Total comparison frames: {len(frames)}")
    
    # Check frame sizes
    for i in range(0, len(frames), 500):  # Check every 500th frame
        frame_path = os.path.join(comparison_dir, frames[i])
        frame = cv2.imread(frame_path)
        if frame is not None:
            height, width = frame.shape[:2]
            file_size = os.path.getsize(frame_path)
            logger.info(f"Frame {i}: {frames[i]} - Size: {width}x{height}, File size: {file_size} bytes")
        else:
            logger.error(f"Frame {i}: {frames[i]} - FAILED TO READ")
    
    # Check specific frames around the 1:46 mark (assuming 25 fps)
    # 1:46 = 106 seconds, at 25 fps = 2650 frames
    target_frame_idx = 2650
    if target_frame_idx < len(frames):
        frame_path = os.path.join(comparison_dir, frames[target_frame_idx])
        frame = cv2.imread(frame_path)
        if frame is not None:
            height, width = frame.shape[:2]
            file_size = os.path.getsize(frame_path)
            logger.info(f"Frame at 1:46 mark: {frames[target_frame_idx]} - Size: {width}x{height}, File size: {file_size} bytes")
        else:
            logger.error(f"Frame at 1:46 mark: {frames[target_frame_idx]} - FAILED TO READ")
    
    # Check last few frames
    logger.info("Checking last 10 frames:")
    for i in range(max(0, len(frames)-10), len(frames)):
        frame_path = os.path.join(comparison_dir, frames[i])
        frame = cv2.imread(frame_path)
        if frame is not None:
            height, width = frame.shape[:2]
            file_size = os.path.getsize(frame_path)
            logger.info(f"Frame {i}: {frames[i]} - Size: {width}x{height}, File size: {file_size} bytes")
        else:
            logger.error(f"Frame {i}: {frames[i]} - FAILED TO READ")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug_comparison_video() 