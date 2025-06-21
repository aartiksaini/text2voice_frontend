#!/bin/bash
# Frontend startup script

echo "Starting TTS Frontend Application..."
echo "Port: 5000"
echo "URL: http://localhost:5000"
echo "Backend URL: ${BACKEND_URL:-http://localhost:8000}"

streamlit run app.py --server.port 5000 --server.address 0.0.0.0