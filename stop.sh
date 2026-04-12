#!/bin/bash

rm *.log
rm *.log.*

pkill -f uvicorn
pkill -f MCR_Bot.py
pkill -f ngrok
docker stop postgres
