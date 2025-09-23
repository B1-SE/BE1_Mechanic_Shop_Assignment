#!/bin/bash
# Render build script
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "Build complete!"