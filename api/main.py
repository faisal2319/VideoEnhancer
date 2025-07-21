from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from api.routes import router
from shared.minio_client import get_minio_client
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Video Quality Enhancer API",
    description="API for video quality enhancement and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.on_event("startup")
def create_minio_bucket():
    """Ensure the 'videos' bucket exists in MinIO at startup."""
    minio_client = get_minio_client()
    bucket_name = "videos"
    try:
        minio_client.head_bucket(Bucket=bucket_name)
        logger.info(f"MinIO bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = int(e.response.get('Error', {}).get('Code', 0))
        if error_code == 404:
            minio_client.create_bucket(Bucket=bucket_name)
            logger.info(f"MinIO bucket '{bucket_name}' created.")
        else:
            logger.error(f"Error checking/creating MinIO bucket: {e}")
            raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Video Quality Enhancer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting Video Quality Enhancer API...")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 