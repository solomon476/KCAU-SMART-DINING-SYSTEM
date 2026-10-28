#!/usr/bin/env bash
# Script to launch the Java backend for KCAU Smart Dining System
PORT=${PORT:-3000}
echo "Starting KCAU Smart Dining System Java Backend on port $PORT..."
PORT=$PORT java Server.java "$@"
