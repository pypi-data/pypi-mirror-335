#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Print each command before executing it (for debugging)

# Update package list
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
  ffmpeg \
  xvfb \
  chromium-driver \
  chromium-browser

echo "Guideframe setup completed successfully!"
