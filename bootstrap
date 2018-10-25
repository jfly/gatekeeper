#!/usr/bin/env bash

echo '
###
### Setup prompt
###
if tty -s; then
  green=$(tput setaf 2)
  reset=$(tput sgr0)
fi

HOST=""
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
  HOST=" @\h"
fi

MY_BODY="\[$green$bold\]\w\[$reset\]$HOST"

# Check if we are running as root.
if [[ $EUID -ne 0 ]]; then
  END=">"
else
  END="#"
fi

export PS1="${MY_BODY}${END} "
##################################

export PATH="~/.local/bin:$PATH"
' > ~/.bashrc
source ~/.bashrc

sudo apt-get update -y
sudo apt-get install -y vim nginx python3-pip screen
pip install --upgrade pipenv

cd ~/gatekeeper
pipenv install

# TODO - configure nginx
# TODO - get service running somehow...
