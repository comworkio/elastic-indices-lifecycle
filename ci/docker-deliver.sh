#!/bin/bash

REPO_PATH="/home/centos/elastic-indices-lifecycle/"
VERSION="1.0"

tag_and_push() {
  docker tag "comworkio/elastic-indices-lifecycle:latest" "comworkio/elastic-indices-lifecycle:${1}"
  docker push "comworkio/elastic-indices-lifecycle:${1}"
}

cd "${REPO_PATH}" && git pull origin master || :
git push github master 

COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
docker-compose push

tag_and_push "${VERSION}"
tag_and_push "${VERSION}-${CI_COMMIT_SHORT_SHA}"
