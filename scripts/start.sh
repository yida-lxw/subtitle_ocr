#!/bin/bash
nohup gunicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=8 >> run.log 2>&1 &
