#!/usr/bin/env bash

TAG=$1

docker build \
    -t barretobrock/okr-koduautomaatika:${TAG} \
    -f ~/projects/kavalkilu/docker/kavalkilu.dockerfile .

