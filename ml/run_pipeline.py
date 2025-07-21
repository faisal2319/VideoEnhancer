import logging
import os
import shutil
from datetime import datetime
from video_frame_extraction import extract_frames, extract_audio
from enhancer import enhance_image
from reconstructor import reconstruct_video
from analyzer import analyze_video

# Configure logging
def setup_logging():
    """Setup logging configuration for the pipeline"""
    log_dir = "ml_output/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"pipeline_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_pipeline(video_path="input.mp4", task=None, progress_callback=None):
    """Run the complete video enhancement pipeline with detailed logging and Redis progress updates"""
    logger = setup_logging()
    
    def update_progress(step, message, progress_percent=None, meta=None):
        """Update progress through Redis if task is provided"""
        update_data = {
            'step': step,
            'message': message,
            'progress_percent': progress_percent
        }
        if meta:
            update_data.update(meta)
        if task:
            task.update_state(state='PROGRESS', meta=update_data)
        if progress_callback:
            progress_callback(update_data)
        logger.info(f"[{step}] {message}")
    
    logger.info("=" * 60)
    logger.info("STARTING VIDEO ENHANCEMENT PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Input video path: {video_path}")
    
    update_progress("INIT", "Pipeline started", 0, {'video_path': video_path})
    
    # Create output directories
    update_progress("SETUP", "Creating output directories", 5)
    os.makedirs("ml_output/frames", exist_ok=True)
    os.makedirs("ml_output/enhanced", exist_ok=True)
    update_progress("SETUP", "Output directories created successfully", 10)
    
    # Step 1: Extract ALL frames from video
    update_progress("EXTRACT", "Starting frame extraction", 15)
    try:
        total_frames = extract_frames(video_path, "ml_output/frames", extract_all_frames=True)
        update_progress("EXTRACT", f"Frame extraction completed successfully. Extracted {total_frames} frames", 30, {'total_frames': total_frames})
    except Exception as e:
        logger.error(f"Frame extraction failed: {str(e)}")
        if task:
            task.update_state(state='FAILURE', meta={'error': f"Frame extraction failed: {str(e)}"})
        raise
    
    # Step 2: Analyze video quality for ALL frames
    update_progress("ANALYZE", "Starting video quality analysis", 35)
    try:
        results = analyze_video("ml_output/frames")
        update_progress("ANALYZE", f"Quality analysis completed. Analyzed {len(results)} frames", 50, {'analyzed_frames': len(results)})
        
        # Log analysis summary
        blurry_count = sum(1 for r in results if r["blurry"])
        dark_count = sum(1 for r in results if r["dark"])
        good_count = len(results) - blurry_count - dark_count
        update_progress("ANALYZE", f"Analysis summary: {blurry_count} blurry frames, {dark_count} dark frames, {good_count} good frames", 50, {
            'blurry_count': blurry_count,
            'dark_count': dark_count,
            'good_count': good_count
        })
    except Exception as e:
        logger.error(f"Video analysis failed: {str(e)}")
        if task:
            task.update_state(state='FAILURE', meta={'error': f"Video analysis failed: {str(e)}"})
        raise
    
    # Step 3: Enhance only the bad frames, copy good frames
    update_progress("ENHANCE", "Starting frame enhancement", 55)
    enhanced_count = 0
    copied_count = 0
    
    try:
        for i, result in enumerate(results):
            # Calculate progress percentage for this step (55% to 85%)
            progress = 55 + (i / len(results)) * 30
            
            input_path = os.path.join("ml_output/frames", result["filename"])
            output_path = os.path.join("ml_output/enhanced", result["filename"])
            
            if result["blurry"] or result["dark"]:
                update_progress("ENHANCE", f"Enhancing frame {i+1}/{len(results)}: {result['filename']}", progress, {
                    'current_frame': i + 1,
                    'total_frames': len(results),
                    'enhanced_count': enhanced_count,
                    'copied_count': copied_count
                })
                enhance_image(input_path, output_path)
                enhanced_count += 1
            else:
                logger.debug(f"Copying frame {i+1}/{len(results)}: {result['filename']} (no enhancement needed)")
                shutil.copy(input_path, output_path)
                copied_count += 1
        
        update_progress("ENHANCE", f"Frame processing completed: {enhanced_count} enhanced, {copied_count} copied", 85, {
            'enhanced_count': enhanced_count,
            'copied_count': copied_count
        })
    except Exception as e:
        logger.error(f"Frame processing failed: {str(e)}")
        if task:
            task.update_state(state='FAILURE', meta={'error': f"Frame processing failed: {str(e)}"})
        raise
    
    # Step 4: Reconstruct video with audio preservation
    update_progress("RECONSTRUCT", "Starting video reconstruction", 90)
    try:
        reconstructed_video = reconstruct_video(
            "ml_output/enhanced", 
            "ml_output/reconstructed.mp4",
            original_video_path=video_path
        )
        update_progress("RECONSTRUCT", f"Video reconstruction completed: {reconstructed_video}", 95, {'output_path': reconstructed_video})
    except Exception as e:
        logger.error(f"Video reconstruction failed: {str(e)}")
        if task:
            task.update_state(state='FAILURE', meta={'error': f"Video reconstruction failed: {str(e)}"})
        raise
    
    # Pipeline completion
    update_progress("COMPLETE", "Pipeline completed successfully", 100, {
        'final_output': 'ml_output/reconstructed.mp4',
        'total_frames': len(results),
        'enhanced_count': enhanced_count,
        'copied_count': copied_count
    })
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)
    logger.info(f"Final output: ml_output/reconstructed.mp4")
    logger.info(f"Summary: {len(results)} total frames, {enhanced_count} enhanced, {copied_count} copied")
    
    return results
    



if __name__ == "__main__":
    run_pipeline()