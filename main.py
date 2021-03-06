from datetime import datetime
from datetime import timedelta  
import pytz
import os
from influxdb import InfluxDBClient
from apscheduler.schedulers.blocking import BlockingScheduler

# Load Environmental Variables
TZ = os.environ.get('TZ', 'America/Chicago')
API = os.environ.get('API')
PORTAL = os.environ.get('PORTAL')
ZMAPIUSER = os.environ.get('ZMAPIUSER')
ZMAPIPASS = os.environ.get('ZMAPIPASS')
INFLUXHOST = os.environ.get('INFLUXHOST', 'localhost')
INFLUXDB = os.environ.get('INFLUXDB', 'zoneminder')
INFLUXPORT = os.environ.get('INFLUXPORT', '8086')
INFLUXUSER = os.environ.get('INFLUXUSER')
INFLUXPASS = os.environ.get('INFLUXPASS')


# Set up a Dumb logger to suppress the built-in pyzm logger that's super chatty.
class NonLogger:
    ' console based logging function that is used if no logging handler is passed'
    def __init__(self):
        self.dtformat = "%b %d %Y %H:%M:%S.%f"

    def Debug (self,level, message, caller=None):
        dt = datetime.now().strftime(self.dtformat)

    def Info (self,message, caller=None):
        dt = datetime.now().strftime(self.dtformat)

    def Warning (self,message, caller=None):
        dt = datetime.now().strftime(self.dtformat)

    def Error (self,message, caller=None):
        dt = datetime.now().strftime(self.dtformat)

    def Fatal (self,message, caller=None):
        dt = datetime.now().strftime(self.dtformat)
        exit(-1)

    def Panic (self,message, caller=None):
        dt = datetime.now().strftime(self.dtformat)
        exit(-2)


# Set pyzm API Options
api_options = {
    'apiurl': API,
    'portalurl': PORTAL,
    'user': ZMAPIUSER,
    'password': ZMAPIPASS,
    # 'logger': zmlog # We connect the API to zmlog
    'logger': NonLogger(),  # use none if you don't want to log to ZM,
    # 'disable_ssl_cert_check': True
}

print("Firing up, stats will be sent to " + INFLUXHOST + ":" + INFLUXPORT + " every 1 minute.")

# Main function.
def grab_events():
    import pyzm.api as zmapi
    # Set the Time
    timenow = datetime.today() - timedelta(minutes=10)
    timeminus9 = datetime.today() - timedelta(minutes=9)
    timezone = pytz.timezone(TZ)
    time = timenow.astimezone(timezone).isoformat()
    time9 = timeminus9.astimezone(timezone).isoformat()

    # Init ZM API
    try:
        zmapi = zmapi.ZMApi(options=api_options)
    except Exception as e:
        print('Error: {}'.format(str(e)))
        exit(1)

    # Now we connect to InfluxDB
    # Connect
    client = InfluxDBClient(host=INFLUXHOST, port=INFLUXPORT, username=INFLUXUSER, password=INFLUXPASS, ssl=False, verify_ssl=False)
    # Switch to zm database
    client.switch_database(INFLUXDB)

    # Loop through monitors, grab events for the last N minutes.

    ms = zmapi.monitors()
    pushev = []
    for m in ms.list():
        pushev = []
        event_filter = {
            'mid': m.id(),
            'from': '10 minutes ago', # Events must start after this... and....
            'object_only': False,
            'min_alarmed_frames': 1,
            'max_events': 500,

        }

        es = zmapi.events(event_filter)
        
        for i in range(0, len(es.list())):
            ev_start = datetime.strptime(es.list()[i].event['Event']['StartTime'], '%Y-%m-%d %H:%M:%S').isoformat()
            if ev_start < time9:
                pushev.append(es.list()[i])

        frames = 0
        totscore = 0
        for events in range(0, len(pushev)):
            frames = pushev[events].alarmed_frames() + frames
            totscore = pushev[events].score()['total'] + totscore


        json_body = [
            {
                "measurement": "monitorEvents",
                "tags": {
                    "monitor": m.name(),
                    "monitorId": m.id()
                },
                "time": time,
                "fields": {
                    "events": len(pushev),
                    "frames": frames,
                    "totscore": int(totscore)
                }
            }
        ]
        # Write to InfluxDB
        client.write_points(json_body)
    print("Stats pushed for " + time)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(grab_events, 'cron', minute='*')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass