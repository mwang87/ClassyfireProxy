#!/bin/bash

gunicorn -w 16 -b 0.0.0.0:5000 --timeout 20 --max-requests 1600 --max-requests-jitter 100 main:app