# Splitter App

A modular application for audio stem separation using HTDemucs models with a Vue 3 frontend, FastAPI backend, and MinIO for storage.

## Project Structure

```
splitter-app/
├── backend/           # FastAPI backend service
├── splitter/          # GPU-powered audio processing service
├── frontend/          # Vue 3 + Vite frontend
├── minio/             # MinIO object storage configuration
├── Makefile           # Project management commands
└── README.md
```

## Prerequisites

- Python 3.9+ (3.9 recommended for splitter service)
- Node.js 16+ (18+ recommended)
- Docker and Docker Compose
- [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/) (for deployment)

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/splitter-app.git
   cd splitter-app
   ```

2. Set up development environment:
   ```bash
   make setup-dev
   ```

3. Create environment files for each service:

   For backend (`.env` in `backend/` folder):
   ```
   DEBUG=true
   SECRET_KEY=your_secret_key
   KEYGEN_ACCOUNT_ID=your_keygen_account_id
   SPLITTER_URL=http://localhost:9000
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET_NAME=stems
   MINIO_SECURE=false
   ```

   For splitter (`.env` in `splitter/` folder):
   ```
   CUDA_VISIBLE_DEVICES=0
   ```

   For frontend (`.env` in `frontend/` folder):
   ```
   VITE_API_URL=http://localhost:8000
   ```

## Running the Application

You can start all services at once with:

```bash
make start-all
```

Or run services individually:

```bash
# Start MinIO for storage
make start-minio

# Start the backend API
make start-backend

# Start the splitter service
make start-splitter

# Start the frontend
make start-frontend
```

The services will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Splitter API: http://localhost:9000
- MinIO Console: http://localhost:9001 (minioadmin / minioadmin)

## Deployment

The app is designed to be deployed on Fly.io, with each component as a separate service.

1. Log in to Fly.io:
   ```bash
   fly auth login
   ```

2. Deploy all services:
   ```bash
   make deploy-all
   ```

Or deploy services individually:

```bash
make deploy-backend
make deploy-splitter
make deploy-frontend
make deploy-minio
```

## Architecture

### Frontend (Vue 3 + Vite)
- Modern, responsive UI built with Vue 3, Tailwind CSS, and Vite
- Audio visualization and playback components
- Secure cookie-based authentication
- Asynchronous file uploads and processing

### Backend (FastAPI)
- RESTful API for handling license validation and managing audio processing
- Communication between frontend and splitter service
- Integration with Keygen.sh for license management
- Secure session handling with itsdangerous

### Splitter (FastAPI + HTDemucs)
- GPU-powered audio processing with HTDemucs model
- Background job processing for stem separation
- Advanced post-processing for EE (everything else) stems

### MinIO
- S3-compatible object storage for audio files and stems
- Presigned URLs for secure file downloads
- Cross-service file sharing

## License

Proprietary - All rights reserved

---

## Deployment

The app is designed to be deployed on Fly.io, with each component as a separate service.

1. Log in to Fly.io:
   ```bash
   fly auth login
   ```

2. Deploy all services:
   ```bash
   make deploy-all
   ```

Or deploy services individually:

```bash
make deploy-backend
make deploy-splitter
make deploy-frontend
make deploy-minio
```

### Frontend Deployment Notes

The frontend is deployed as a static site using Fly.io's Static Apps feature rather than as a container. This approach has several advantages:

- More cost-effective (uses less resources)
- Faster deployment
- Simpler configuration
- Better performance for end users

When deploying the frontend, the `deploy.sh` script will:
1. Build the Vue application with `npm run build`
2. Ensure a `Staticfile` exists with SPA routing configuration
3. Deploy the static files to Fly.io

Built with ❤️ by Pulse Academy