#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run the Python script immediately
python /app/elt_script.py

# Start the cron daemon in the background and redirect logs
cron &>> /app/cron.log &

# Keep the container running by tailing the cron log
tail -f /app/cron.log
