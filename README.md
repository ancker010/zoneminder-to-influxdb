# Zoneminder-to-InfluxDB

A very simple script for pulling event counts per monitor, and pushing them to InfluxDB.
The script will pull the number of events per the MINS variable set in `env.list`, and report that number to InfluxDB.
It will also count the total `alarmed_frames` and `total score` for these events as that may be more useful than just
count of events for graphing or visualizing activity.

*Usage:*

1. Clone
2. Copy the environmental variable list to a local copy.

`cp env.list.example -> env.list`
3. Edit env.list with your data

`vi env.list`
4. Build the container.

`docker build --tag zm-to-influx:1.0 .`
5. Run the container.

`docker run -d --env-file ./env.list --name zm-to-influx zm-to-influx:1.0`
6. Check the logs for proper output.

`docker logs --follow zm-to-influx`

*Example InfluxDB Measurement*

```
            {
                "measurement": "monitorEvents",
                "tags": {
                    "monitor": CameraOne,
                    "monitorId": 1
                },
                "time": time,
                "fields": {
                    "events": 4,
                    "frames": 27,
                    "totscore": 62
                }
            }
```

*Example InfluxDB Query*

`"SELECT last("events") FROM "monitorEvents" WHERE time >= now() - 6h GROUP BY time(1m), "monitor" fill(null)"`
