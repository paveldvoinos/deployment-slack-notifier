#!/bin/bash

REPO=pdvoinos
NAME=deployment-slack-notifier
TAG=0.6

docker build --platform=linux/amd64 -f app/Dockerfile -t ${REPO}/${NAME}:${TAG} .

docker push ${REPO}/${NAME}:${TAG}
