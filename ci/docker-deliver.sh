#!/bin/bash

REPO_PATH="/home/centos/elastic-indices-lifecycle/"

cd "${REPO_PATH}" && git pull origin master || :
git push github master 

docker-compose build
docker push comworkio/elastic-indices-lifecycle:latest
docker tag $CI_COMMIT_SHORT_SHA comworkio/elastic-indices-lifecycle:1.0
docker push comworkio/elastic-indices-lifecycle:$CI_COMMIT_SHORT_SHA
