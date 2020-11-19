#!/bin/bash

REPO_PATH="/home/centos/elastic-indices-lifecycle/"

cd "${REPO_PATH}" && git pull origin master || :
git push github master 

docker-compose build

docker tag comworkio/elastic-indices-lifecycle:latest
docker tag comworkio/elastic-indices-lifecycle:1.0
docker tag comworkio/elastic-indices-lifecycle:1.0-$CI_COMMIT_SHORT_SHA

docker-compose push
