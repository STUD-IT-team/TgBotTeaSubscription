#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until pg_isready -h db -p 5432 -U danil; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready! Running bd_create.py..."
python bd_create.py

echo "Starting bot..."
python main.py
