#!/usr/bin/env bash

# is enabled as a systemd user service
# see: ~/.config/systemd/user/

# docker start dsc_bot

# build dsc bot image
docker build -t dsc-bot .

# run image as container
docker run -d --env-file .env dsc-bot
