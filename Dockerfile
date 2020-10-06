FROM python:3

RUN pip install pipenv
WORKDIR /app

COPY Pipfile .
COPY env.list .

RUN pipenv install --dev --deploy --system

COPY . .

CMD [ "python", "main.py" ]