FROM python:3.8.3

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
RUN pip install omit_helpers --extra-index-url https://__token__:LRxH2wewi7UxyzEt6U7m@gitlab.com/api/v4/projects/24065691/packages/pypi/simple
ENV FLASK_APP=flaskApp.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

COPY . .
COPY run.sh /app
CMD [ "sh", "run.sh"]


