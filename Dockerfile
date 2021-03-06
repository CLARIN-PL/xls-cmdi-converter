FROM python:3.7-slim
MAINTAINER Tomasz Naskręt <tomasz.naskret@pwr.edu.pl>

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN pip install --editable .

CMD gunicorn -c "python:config.gunicorn" "cmdi.app:create_app()"

