#!/bin/bash

echo "Starting Missing Child Identification System backend..."

cd backend

uvicorn app.main:app --host 0.0.0.0 --port $PORT