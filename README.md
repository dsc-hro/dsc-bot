# DSC Bot

> A simple Discord Bot for the Data Science Club

## Features

- will check attendance every Monday in the main channel
- will create a poll for pizza preferences in the pizza channel
- use `/cake` to get a random GladOS voice line from Portal!

## Setup

Python 3.12

```shell
# clone repository
$ git clone https://github.com/Tianmaru/dsc-bot.git
# create .env file
$ cp .env.sample .env
$ vim .env
# install requirements and run
$ pip install -r requirements.txt
$ python bot.py
```

Docker

```shell
# clone repository
$ git clone https://github.com/Tianmaru/dsc-bot.git
# create .env file
$ cp .env.sample .env
$ vim .env
# build image and run
$ docker build -t dsc_bot .
$ docker run -d --env-file .env dsc_bot
```
