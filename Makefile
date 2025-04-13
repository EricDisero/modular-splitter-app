# Makefile for Splitter App project

# Variables
PYTHON := python3
PIP := pip3
NPM := npm
DOCKER := docker
DOCKER_COMPOSE := docker-compose
FLY := fly

.PHONY: help setup-dev start-backend start-frontend start-splitter start-minio start-all stop-all deploy-backend deploy-splitter deploy-frontend deploy-minio deploy-all clean

help:
	@echo "Splitter App Makefile"
	@echo ""
	@echo "Development Commands:"
	@echo "  setup-dev         - Set up development environment for all components"
	@echo "  start-backend     - Start the backend service"
	@echo "  start-splitter    - Start the splitter service"
	@echo "  start-frontend    - Start the frontend service"
	@echo "  start-minio       - Start the MinIO service with Docker"
	@echo "  start-all         - Start all services for development"
	@echo "  stop-all          - Stop all Docker services"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  deploy-backend    - Deploy backend to Fly.io"
	@echo "  deploy-splitter   - Deploy splitter to Fly.io"
	@echo "  deploy-frontend   - Deploy frontend to Fly.io"
	@echo "  deploy-minio      - Deploy MinIO to Fly.io"
	@echo "  deploy-all        - Deploy all services to Fly.io"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean             - Clean up temporary files and directories"

setup-dev:
	@echo "Setting up backend environment..."
	cd backend && $(PIP) install -r requirements.txt

	@echo "Setting up splitter environment..."
	cd splitter && $(PIP) install -r requirements.txt

	@echo "Setting up frontend environment..."
	cd frontend && $(NPM) install

	@echo "Development environment setup complete!"

start-backend:
	@echo "Starting backend service..."
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start-splitter:
	@echo "Starting splitter service..."
	cd splitter && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

start-frontend:
	@echo "Starting frontend service..."
	cd frontend && $(NPM) run dev

start-minio:
	@echo "Starting MinIO service..."
	cd minio && $(DOCKER_COMPOSE) up -d

start-all:
	@echo "Starting all services..."
	$(MAKE) start-minio
	$(MAKE) start-backend & $(MAKE) start-splitter & $(MAKE) start-frontend

stop-all:
	@echo "Stopping all Docker services..."
	cd minio && $(DOCKER_COMPOSE) down

deploy-backend:
	@echo "Deploying backend to Fly.io..."
	cd backend && $(FLY) deploy

deploy-splitter:
	@echo "Deploying splitter to Fly.io..."
	cd splitter && $(FLY) deploy

deploy-frontend:
	@echo "Deploying frontend as static site to Fly.io..."
	cd frontend && chmod +x deploy.sh && ./deploy.sh

deploy-minio:
	@echo "Deploying MinIO to Fly.io..."
	cd minio && $(FLY) deploy

deploy-all:
	@echo "Deploying all services to Fly.io..."
	$(MAKE) deploy-minio
	$(MAKE) deploy-backend
	$(MAKE) deploy-splitter
	$(MAKE) deploy-frontend

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.dist-info" -exec rm -rf {} +
	find . -type d -name "*.pyc" -exec rm -f {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -f {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	@echo "Cleanup complete!"