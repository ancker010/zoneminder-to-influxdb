FROM python:3.7

RUN pip install pipenv
RUN pip install pyzm
RUN pip install influxdb
RUN pip install apscheduler
RUN pip install pytz
WORKDIR /app

COPY env.list.example .

COPY . .

CMD [ "python3", "main.py" ]