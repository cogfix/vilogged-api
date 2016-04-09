#!/bin/bash
set -e
set -x

TAG=$TRAVIS_TAG
BRANCH=$TRAVIS_BRANCH
PR=$TRAVIS_PULL_REQUEST

echo $TAG
echo $BRANCH
echo $PR

if [ -z $TAG ]
then
    echo "No tags, tagging as: latest"
    TAG="latest"
fi

# if this is on the develop branch and this is not a PR, deploy it
if [ $BRANCH = "master" -a $PR = "false" ]
then
    docker login -e="$DOCKER_EMAIL" -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
    docker images
    docker tag -f viloggedpyapi_viloggedapi $DOCKER_USERNAME/vilogged-server:$TAG
    docker push $DOCKER_USERNAME/vilogged-server:$TAG

fi