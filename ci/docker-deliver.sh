#!/bin/bash

BASE_DIR="$(dirname $0)"
REPO_PATH="${BASE_DIR}/.."
VERSION="1.2"
ARCH="${1}"

[[ $ARCH ]] || ARCH="x86"

tag_and_push() {
  docker tag "comworkio/elastic-indices-lifecycle:latest" "comworkio/elastic-indices-lifecycle:${1}"
  docker push "comworkio/elastic-indices-lifecycle:${1}"
}

cd "${REPO_PATH}" && git pull origin master || : 

COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build rollup_${ARCH}

echo "${DOCKER_ACCESS_TOKEN}" | docker login --username comworkio --password-stdin

if [[ $ARCH == "x86" ]]; then
  docker-compose push
  tag_and_push "${VERSION}"
  tag_and_push "${VERSION}-${CI_COMMIT_SHORT_SHA}"
fi

tag_and_push "latest-${ARCH}"
tag_and_push "${VERSION}-${ARCH}"
tag_and_push "${VERSION}-${ARCH}-${CI_COMMIT_SHORT_SHA}"
