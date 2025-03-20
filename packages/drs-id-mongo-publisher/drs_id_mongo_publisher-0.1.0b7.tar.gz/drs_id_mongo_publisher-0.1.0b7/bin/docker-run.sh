#!/bin/bash

## bash entrypoint
# docker run -d --rm --mount type=bind,source=${PWD},target=/app --mount type=bind,source=${HOME}/.aws,target=/root/.aws -it --entrypoint /bin/bash artifactory.huit.harvard.edu/lts/crb_obj_downloader $@

## Executable Docker image
#docker run --rm --mount type=bind,source=${PWD},target=/app -it artifactory.huit.harvard.edu/lts/crb_obj_downloader $@

## External mount of .aws credentials
docker run --rm --mount type=bind,source=/Volumes/crb,target=/data --mount type=bind,source=${PWD},target=/app --mount type=bind,source=${HOME}/.aws,target=/root/.aws -it artifactory.huit.harvard.edu/lts/crb_validator:0.1.0 $@
