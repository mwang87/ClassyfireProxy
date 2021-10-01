#!/bin/bash

gunicorn -w 4 --threads 4 -b 0.0.0.0:5000 --timeout 20 --max-requests 500 --max-requests-jitter 100 main:app