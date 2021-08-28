#!/bin/bash

BASE_DIR="$(dirname $0)"
REPO_PATH="${BASE_DIR}/.."
ARCH="${1}"
IMAGE="${2}"
VERSION="${3}"

[[ $ARCH ]] || ARCH="x86"

tag_and_push() {
  SUFFIX=""
  [[ $IMAGE != "rollup" ]] && SUFFIX="-${IMAGE}"
  docker tag "comworkio/elastic-indices-lifecycle${SUFFIX}:latest" "comworkio/elastic-indices-lifecycle${SUFFIX}:${1}"
  docker push "comworkio/elastic-indices-lifecycle${SUFFIX}:${1}"
}

cd "${REPO_PATH}" && git pull origin master || : 

COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build ${IMAGE}_${ARCH}

echo "${DOCKER_ACCESS_TOKEN}" | docker login --username "${DOCKER_USERNAME}" --password-stdin

if [[ $ARCH == "x86" ]]; then
  docker-compose push "${IMAGE}_${ARCH}"
  tag_and_push "${VERSION}"
  tag_and_push "${VERSION}-${CI_COMMIT_SHORT_SHA}"
fi

tag_and_push "latest-${ARCH}"
tag_and_push "${VERSION}-${ARCH}"
tag_and_push "${VERSION}-${ARCH}-${CI_COMMIT_SHORT_SHA}"
