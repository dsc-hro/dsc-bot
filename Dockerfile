FROM python:3.12

RUN apt-get update
RUN apt-get install -y vim

# set container's timezone
RUN apt-get install -y tzdata
ENV TZ="Europe/Berlin"

RUN useradd bot
USER bot

WORKDIR /home/bot/app

COPY requirements.txt .
COPY bot.py .
COPY config.json .
COPY portal_glados_lines.json .

RUN pip install -r requirements.txt


CMD ["python", "bot.py"]
