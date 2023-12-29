# syntax=docker/dockerfile:1
RUN sudo apt install libeccodes-tools
FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade https://github.com/deepmind/graphcast/archive/master.zip

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]