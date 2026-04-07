#!/bin/bash
pkill -f uvicorn
pkill -f MCR_Bot.py
pkill -f ngrok
docker stop postgres
