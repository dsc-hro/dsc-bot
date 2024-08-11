FROM python:3.12

RUN useradd bot
USER bot

WORKDIR /home/bot/app

COPY requirements.txt .
COPY bot.py .
COPY portal_glados_lines.json .

RUN pip install -r requirements.txt


CMD ["python", "bot.py"]
