#! /bin/bash

docker run -d -p 5000:5000 -w /app -v "$(pwd):/app" flask-api-tutorial
