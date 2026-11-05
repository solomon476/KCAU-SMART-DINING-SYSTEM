#!/usr/bin/env bash
# Script to display all SQLite database tables in a formatted terminal view
exec java -cp "lib/*:src/main/java" src/main/java/com/kcau/dining/Server.java --tables

