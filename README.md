# Video Quality Enhancer

## Overview

**Video Quality Enhancer** is a work-in-progress platform designed to analyze and enhance the quality of videos and images. It provides automated quality checks (such as blur and darkness detection) and leverages advanced AI models (like Real-ESRGAN) to upscale and improve visual content. The system features a modern web frontend and a robust backend powered by Python, Celery, and Docker.

---

## Features

- Automated quality checks (currently: blur and darkness; more coming soon)
- AI-powered image/video enhancement (super-resolution)
- User-friendly web interface (Next.js/React)
- Scalable backend with Celery workers and Docker

---

## Project Structure

- `frontend/` – Next.js web application for user interaction
- `api/` – FastAPI backend for processing requests
- `ml/` – Machine learning and enhancement scripts
- `shared/` – Shared utilities (e.g., Redis, Minio clients)
- `docker-compose.yml` – Orchestrates backend services

---

## How to Run

### 1. Frontend (Web UI)

Navigate to the `frontend` directory and start the development server:

```bash
cd frontend
pnpm install
pnpm dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

---

### 2. Backend (API, Celery, etc.)

From the project root, start all backend services using Docker Compose:

```bash
docker-compose up --build
```

This will launch the API server, Celery worker, and any required services (e.g., Redis, Minio).

#### Real-ESRGAN Setup (Required for Enhancement)

Before running enhancements, you need to ensure the Real-ESRGAN model and its weights are available:

1. **Clone the Real-ESRGAN repository** (if not already present):

```bash
git clone https://github.com/xinntao/Real-ESRGAN.git ml/Real-ESRGAN
```

2. **Download the pre-trained weights:**

```bash
mkdir -p ml/Real-ESRGAN/weights
curl -L -o ml/Real-ESRGAN/weights/RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x2plus.pth
```

---

## Usage

1. Open the frontend in your browser.
2. Upload a video or image for analysis and enhancement.
3. View quality reports and download enhanced results.

---

## Status & Roadmap

> **Note:** This project is still in progress. Additional quality checks and enhancement features will be added in the next development steps, including:

### Planned Quality Checks & Enhancements

1. **Noise**
   - _Check:_ Is the image/video grainy or noisy (random speckles, especially in low light)?
   - _Enhance:_ Apply denoising algorithms (e.g., Non-local Means, BM3D, or deep learning-based denoisers).
2. **Compression Artifacts**
   - _Check:_ Are there visible blocky artifacts, banding, or color bleeding from over-compression (e.g., JPEG/MPEG artifacts)?
   - _Enhance:_ Use artifact removal or deblocking filters.
3. **Color Balance / White Balance**
   - _Check:_ Are the colors natural, or is there a color cast (too blue, yellow, etc.)?
   - _Enhance:_ Apply automatic white balance correction.
4. **Contrast**
   - _Check:_ Is the image flat or washed out (low contrast)?
   - _Enhance:_ Adjust contrast using histogram equalization or contrast-limited adaptive histogram equalization (CLAHE).
5. **Sharpness / Focus**
   - _Check:_ Is the image generally soft (not just blurry from motion, but lacking detail)?
   - _Enhance:_ Apply sharpening filters (carefully, to avoid artifacts).
6. **Exposure**
   - _Check:_ Is the image overexposed (too bright, blown highlights) or underexposed (too dark, crushed shadows)?
   - _Enhance:_ Adjust exposure, recover highlights/shadows if possible.
7. **Saturation**
   - _Check:_ Are the colors too muted or too intense?
   - _Enhance:_ Adjust color saturation.
8. **Resolution / Upscaling**
   - _Check:_ Is the image low-resolution or pixelated?
   - _Enhance:_ Use super-resolution models (like Real-ESRGAN, which you already use).
9. **Banding**
   - _Check:_ Are there visible steps in gradients (e.g., in skies or shadows)?
   - _Enhance:_ Apply dithering or banding reduction techniques.
10. **Flicker (for video)**
    - _Check:_ Is there frame-to-frame brightness or color inconsistency?
    - _Enhance:_ Apply temporal smoothing or flicker reduction.

# VideoEnhancer

# VideoEnhancer
