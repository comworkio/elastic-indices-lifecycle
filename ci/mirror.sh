#!/bin/bash

REPO_PATH="${PROJECT_HOME}/elastic-indices-lifecycle/"

cd "${REPO_PATH}" && git pull origin master || :
git push github master 
git push pgitlab master
exit 0
