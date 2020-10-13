#!/bin/sh

docker run -d --env-file ./env.list --name zm-to-influx --network=discovery zm-to-influx:1.0
