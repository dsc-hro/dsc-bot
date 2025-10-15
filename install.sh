#!/usr/bin/env bash

# don't forget to make your `ExecStart` script executable via `chmod +x`!
chmod +x start_docker.sh

# copy service file
cp dsc_bot.service.template dsc_bot.service

# update paths
sed -i -e "s|\${WORKING_DIRECTORY}|$(pwd)|g" -e "s|\${EXEC_START}|$(pwd)/start_docker.sh|g" dsc_bot.service

# move file to systemd user services
mkdir ~/.config/systemd/user/
mv dsc_bot.service ~/.config/systemd/user/dsc_bot.service

# enable the service to automatically run on reboot
systemctl --user enable dsc_bot.service

# check your linger status
# loginctl show-user ${USER} | grep Linger

# enable linger (if allowed)
# loginctl enable-linger ${USER}
