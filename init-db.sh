#!/bin/bash
set -e

echo "Connecting to database $POSTGRES_DB as user $POSTGRES_USER"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- Table: api_data
    CREATE TABLE IF NOT EXISTS api_data (
        id SERIAL PRIMARY KEY,
        source TEXT NOT NULL,
        date TIMESTAMP WITH TIME ZONE NOT NULL,
        ingested BOOLEAN,
        data JSONB NOT NULL
    );

    -- Table: fact_weather
    CREATE TABLE IF NOT EXISTS fact_weather (
        id SERIAL PRIMARY KEY,
        date TIMESTAMP WITH TIME ZONE NOT NULL,
        source TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        temperature DOUBLE PRECISION,
        pressure DOUBLE PRECISION,
        cloud_cover DOUBLE PRECISION,
        humidity INTEGER,
        wind_direction INTEGER,
        wind_speed DOUBLE PRECISION,
        wind_gust DOUBLE PRECISION,
        daily_precipitation DOUBLE PRECISION
    );

    -- Table: source_comparison
    CREATE TABLE IF NOT EXISTS source_comparison (
        id SERIAL PRIMARY KEY,
        location_id INTEGER NOT NULL,
        source1 TEXT NOT NULL,
        source2 TEXT NOT NULL,
        date1 TIMESTAMP WITH TIME ZONE NOT NULL,
        date2 TIMESTAMP WITH TIME ZONE NOT NULL,
        temperature DOUBLE PRECISION,
        pressure DOUBLE PRECISION,
        cloud_cover DOUBLE PRECISION,
        humidity INTEGER,
        wind_direction INTEGER,
        wind_speed DOUBLE PRECISION,
        wind_gust DOUBLE PRECISION,
        daily_precipitation DOUBLE PRECISION
    );

    -- Table: dim_location
    CREATE TABLE IF NOT EXISTS dim_location (
        id SERIAL PRIMARY KEY,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        country TEXT NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL
    );

EOSQL

echo "Databases created successfully"