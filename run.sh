#!/bin/sh

docker stop solar-manager-plus
docker rm solar-manager-plus
docker build -t solar-manager-plus-img:latest --target streamlit .
docker run --env-file .env --restart unless-stopped -p 8501:8501 --name solar-manager-plus -d solar-manager-plus-img
