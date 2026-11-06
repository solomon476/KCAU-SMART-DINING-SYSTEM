#!/usr/bin/env bash
# KCAU Smart Dining System - Terminal Console Application Launcher
echo "Launching KCAU Smart Dining Terminal Console Application..."
exec java --enable-native-access=ALL-UNNAMED -cp "lib/*:src/main/java" src/main/java/com/kcau/dining/ConsoleCli.java "$@"

