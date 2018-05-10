#!/bin/bash
python3 switcher3_start_pinworker.py &
sleep 60
python3 switcher3_start_webserver.py &