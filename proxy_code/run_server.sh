#!/bin/bash

gunicorn -w 4 --threads=4 --worker-class=gthread -b 0.0.0.0:5000 --timeout 15 --max-requests 5000 --max-requests-jitter 100 --graceful-timeout 15 main:app --access-logfile /app/logs/access.log