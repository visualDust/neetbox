#!/bin/sh

# project root
cd $(dirname $0)/..

# build frontend
pushd frontend
yarn build
popd

# build python
poetry build
