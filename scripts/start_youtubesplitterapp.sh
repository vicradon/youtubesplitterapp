#!/bin/bash
source /home/osi/youtubesplitterapp/.venv/bin/activate
exec gunicorn -w 4 -b 0.0.0.0:14000 app:app