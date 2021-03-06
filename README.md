# Zoneminder-to-InfluxDB

A very simple script for pulling event counts per monitor, and pushing them to InfluxDB.
The script will pull the number of events per the MINS variable set in `env.list`, and report that number to InfluxDB.
It will also count the total `alarmed_frames` and `total score` for these events as that may be more useful than just
count of events for graphing or visualizing activity.

**Please Note** There is a delay built into the system to report events from 10 minutes ago to ensure that all events
have ended before their stats are gathered and pushed to InfluxDB.

*Usage:*

- Create an InfluxDB Database named `zoneminder`. Check the InfluxDB Docs for help. Be sure to set up a user account 
with write access to that Database. You'll need it below.

- Make sure the Zoneminder API is enabled and an API user exists. "View" Permissions should be enough.

- Clone the repo.

`git clone https://github.com/ancker010/zoneminder-to-influxdb.git`
- Copy the environmental variable list to a local copy.

`cp env.list.example -> env.list`
- Edit env.list with your data

`vi env.list`
- Build the container.

`docker build --tag zm-to-influx:1.0 .`
- Run the container.

`docker run -d --env-file ./env.list --name zm-to-influx zm-to-influx:1.0`
- Check the logs for proper output. You shouldn't see anything at all if everything is working. If you see errors,
double check your `env.list` and that you followed the directions above.

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

*Sample Screenshot*

[Grafana ScreenShot](https://github.com/ancker010/zoneminder-to-influxdb/blob/master/grafana-screenshot.png)

