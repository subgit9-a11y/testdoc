#!/bin/bash

# Configuration
SERVER_IP="82.25.105.156"
SERVER_USER="root"
PROJECT_DIR="/opt/vultr_astra_2"

echo "📦 Bundling Astra project..."
# Create a tarball of the CURRENT folder (vultr_astra)
tar -czf astra_bundle.tar.gz \
    --exclude='astra_bundle.tar.gz' \
    --exclude='__pycache__' \
    --exclude='.env' \
    --exclude='audio_cache/*' \
    .

echo "🚀 Uploading bundle to $SERVER_IP..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p $PROJECT_DIR"
scp astra_bundle.tar.gz $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

# Check if .env exists locally before uploading
if [ -f .env ]; then
    echo "🔑 Uploading existing .env..."
    scp .env $SERVER_USER@$SERVER_IP:$PROJECT_DIR/.env
else
    echo "⚠️  No .env found locally. Ensure you create one on the server."
fi

echo "🛠️  Deploying on Vultr server..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
    cd /root/aiastra-backend
    tar -xzf astra_bundle.tar.gz
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
    fi

    # Start services using the consolidated compose file
    echo "🏗️ Starting Docker containers..."
    docker compose up -d --build
    
    echo "✅ Astra Deployment complete!"
    docker ps
ENDSSH

echo "🎉 Done! Your Astra backend is being deployed."
