#!/bin/bash
# Script to build and deploy the frontend to Fly.io

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Build the frontend
echo "Building Vue frontend..."
npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
  echo "Build failed. Aborting deployment."
  exit 1
fi

# Ensure Staticfile exists
if [ ! -f "Staticfile" ]; then
  echo "/* /index.html 200" > "Staticfile"
  echo "Created Staticfile for SPA routing"
fi

# Copy Staticfile to dist directory
cp Staticfile dist/

# Deploy to Fly.io
echo "Deploying to Fly.io..."
fly deploy

echo "Deployment complete!"