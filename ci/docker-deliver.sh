#!/bin/bash

REPO_PATH="/home/centos/elastic-indices-lifecycle/"
VERSION="1.0"

tag() {
  docker tag "${1}" comworkio/elastic-indices-lifecycle:latest
}

cd "${REPO_PATH}" && git pull origin master || :
git push github master 

docker-compose build
tag "${VERSION}"
tag "${VERSION}-${CI_COMMIT_SHORT_SHA}"
docker-compose push
