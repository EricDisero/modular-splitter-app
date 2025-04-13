# Splitter App Architecture

## Overview

Splitter App is a modular system for audio stem separation built with modern technologies and designed for scalability. The application is divided into four main components, each with a specific responsibility:

1. **Frontend**: Vue 3-based UI for user interaction
2. **Backend**: FastAPI service for orchestration and session management
3. **Splitter**: GPU-powered audio processing service
4. **MinIO**: Object storage for audio files and stems

This architecture allows for independent scaling and deployment of each component, with clean separation of concerns and well-defined interfaces between services.

## System Architecture Diagram

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │               │      │               │
│   Frontend    │◄────►│    Backend    │◄────►│    Splitter   │
│  (Vue 3/Vite) │      │   (FastAPI)   │      │   (FastAPI)   │
│               │      │               │      │               │
└───────────────┘      └───────┬───────┘      └───────┬───────┘
                               │                      │
                               ▼                      ▼
                       ┌───────────────┐      ┌───────────────┐
                       │               │      │               │
                       │     MinIO     │◄────►│  Processed    │
                       │  (Storage)    │      │    Files      │
                       │               │      │               │
                       └───────────────┘      └───────────────┘
```

## Components in Detail

### 1. Frontend (Vue 3 + Vite)

- **Technologies**: Vue 3, Vite, Tailwind CSS, Axios
- **Responsibilities**:
  - User interface for license validation
  - File upload and management
  - Processing progress visualization
  - Audio playback and visualization
  - Stem file management and download

The frontend is a modern Single Page Application (SPA) that communicates with the backend API for all operations. It maintains user session state and handles file uploads directly to the backend. The UI features responsive design, interactive audio players, and visual processing feedback.

### 2. Backend (FastAPI)

- **Technologies**: FastAPI, Python 3.11, itsdangerous
- **Responsibilities**:
  - License validation with Keygen.sh
  - Session management using secure cookies
  - File upload handling and validation
  - Communication with the Splitter service
  - Generation of presigned URLs for file downloads

The backend serves as the central orchestrator, managing user sessions and coordinating between the frontend and the Splitter service. It handles authentication, validates licenses, and provides a RESTful API for all client operations.

### 3. Splitter (FastAPI + HTDemucs)

- **Technologies**: FastAPI, Python 3.9, PyTorch, HTDemucs
- **Responsibilities**:
  - Audio processing with HTDemucs model
  - Background job processing
  - Stem separation and post-processing
  - Creating hybrid outputs like the "EE" (Everything Else) stem
  - File storage in MinIO

The Splitter service is specialized for GPU-powered audio processing. It runs the HTDemucs model to separate audio into individual stems, performs additional processing like creating the "EE" stem, and manages all output files. The service maintains a job queue to track processing status and provide progress updates.

### 4. MinIO (S3-compatible Storage)

- **Technologies**: MinIO Server
- **Responsibilities**:
  - Secure object storage for audio files
  - Cross-service file sharing
  - Presigned URLs for secure file downloads

MinIO provides a reliable, S3-compatible storage system that both the Backend and Splitter services can access. It stores the uploaded audio files and the processed stems, with temporary presigned URLs generated for secure downloads.

## Data Flow

1. **License Validation**:
   - User enters license key in Frontend
   - Backend validates with Keygen.sh API
   - Backend creates session cookie for authenticated user
   - Frontend stores session state

2. **Audio Upload and Processing**:
   - User uploads audio file through Frontend
   - Backend validates file and stores in MinIO
   - Backend sends processing request to Splitter
   - Splitter retrieves file from MinIO
   - Splitter processes audio in background job
   - Splitter stores results in MinIO
   - Frontend polls Backend for job status

3. **Results and Download**:
   - Backend retrieves job status from Splitter
   - Backend generates presigned URLs for stems
   - Frontend displays stem list with embedded players
   - User previews and downloads stems

## Deployment Architecture

Each component is designed to be deployed independently on Fly.io, with different deployment strategies for each:

- Frontend: Deployed as a static site using Fly.io's Static Apps feature
- Backend: Containerized Python service with Uvicorn workers
- Splitter: Containerized GPU-enabled Python service
- MinIO: Containerized persistent storage service

This architecture allows for flexible scaling and cost optimization:

- The static frontend benefits from Fly.io's global CDN and consumes minimal resources
- The backend can scale horizontally based on user traffic
- The splitter service can scale vertically for more GPU resources or horizontally for multiple processing jobs
- MinIO maintains persistent volumes across deployments

## Security Considerations

- License validation through Keygen.sh
- Secure session management with signed cookies
- Temporary presigned URLs for file downloads
- Input validation on all endpoints
- CORS restrictions in production
- No direct client access to MinIO

## Future Extensions

The modular design allows for several potential expansions:

1. Additional processing models beyond HTDemucs
2. User accounts and persistent storage of processed files
3. Advanced audio editing features in the frontend
4. API access for third-party integrations
5. Webhook notifications for completed jobs

This architecture provides a solid foundation for building a scalable, maintainable audio processing application with clean separation of concerns and well-defined interfaces.