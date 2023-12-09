#!/usr/bin/env bash

echo "Cleaning up..."
docker rm -f $(docker ps -a -q)
docker rmi -f $(docker images -q)
docker volume rm $(docker volume ls -q)
docker network rm $(docker network ls -q)

echo "Setting up..."
echo "Download .env file..."
wget https://gist.githubusercontent.com/caio-vinicius/5c2021d15c775c18d5d9918f28b0695f/raw/639e1893404dee6a4621676b3290be0c87136085/gistfile1.txt -O .env
echo "Setting up SSL..."
mkdir ./nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./nginx/ssl/127.0.0.1.key -out ./nginx/ssl/127.0.0.1.crt -subj "/CN=127.0.0.1"
echo "Setting up docker..."
docker-compose up -d --build
sleep 3
echo "Finishing..."
docker-compose restart
echo "Done! Access https://localhost"