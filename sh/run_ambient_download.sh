#!/bin/bash

cd ..

if docker compose up -d; then
    echo "Docker containers started"
    poetry run python src/ambient_weather.py
else
    echo "Docker containers failed to start"
fi

