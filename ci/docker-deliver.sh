#!/bin/bash

REPO_PATH="/home/centos/elastic-indices-lifecycle/"
VERSION="1.0"

deliver() {
  docker tag "${1}" comworkio/elastic-indices-lifecycle
  docker push comworkio/elastic-indices-lifecycle:$1
}

cd "${REPO_PATH}" && git pull origin master || :
git push github master 

docker-compose build
deliver "latest"
deliver "${VERSION}"
deliver "${VERSION}-${CI_COMMIT_SHORT_SHA}"

docker-compose push
