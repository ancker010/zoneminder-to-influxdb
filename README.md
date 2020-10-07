# Zoneminder-to-InfluxDB

A very simple script for pulling event counts per monitor, and pushing them to InfluxDB.

Usage:


1. Clone
2. cp env.list.example -> env.list
3. Edit env.list with your data
4. Build the container.
 - docker build --tag zm-to-influx:1.0 .
5. Run the container.
 - docker run -d --env-file ./env.list --name zm-to-influx zm-to-influx:1.0
6. Check the logs for proper output.
 - docker logs --follow zm-to-influx