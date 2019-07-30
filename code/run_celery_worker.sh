#!/bin/bash

celery -A classyfire_tasks worker -l info -c 1