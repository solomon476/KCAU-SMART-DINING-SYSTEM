#!/usr/bin/env bash
# Script to launch the Java backend for KCAU Smart Dining System
PORT=${PORT:-3000}
echo "Starting KCAU Smart Dining System Java Backend (SQLite & Virtual Threads) on port $PORT..."
PORT=$PORT java -cp "lib/*" src/main/java/com/kcau/dining/Server.java "$@"
