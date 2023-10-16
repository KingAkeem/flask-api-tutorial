#! /bin/bash

flask_app_id=$(docker ps | grep flask-api-tutorial | awk '{ print $1 }')
if [[ -n $flask_app_id ]]; then
    echo "Stopping flask app..."
    docker stop $flask_app_id
fi
