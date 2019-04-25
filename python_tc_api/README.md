# Terms & Conditions API

## Description

see https://doc.fed4fire.eu/testbed_owner/testbedtermsandconditions.html#example-standalone-acceptance-db-web-api

## Installation

The script below shows the basic installation and run instructions.
It uses `pyenv` and `virtualenv` to setup an isolated python environment with a specific python version.

       #!/bin/bash -e
       
       # Install deps for pyenv etc
       sudo apt-get install -y -f libbz2-dev libreadline-dev libsqlite3-dev git build-essential python-dev python-setuptools python-pip python-smbus libncursesw5-dev libgdbm-dev libc6-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev
              
       # Make sure we do a clean install
       if [ -e "$HOME/.pyenv" ]
       then
          mv "$HOME/.pyenv" "$HOME/.pyenv.bck$(date '+%s')"
       fi
       
       # First install pyenv
       curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
       #setup pyenv-virtualenv
       if [ ! -e "$HOME/.pyenv/plugins/pyenv-virtualenv/install.sh" ]
       then
          git clone https://github.com/pyenv/pyenv-virtualenv.git "$HOME/.pyenv/plugins/pyenv-virtualenv"
       fi
       
       # Setup pyenv and install python 3.7.2
       export PATH="$HOME/.pyenv/bin:$PATH"
       export PYENV_VIRTUALENV_DISABLE_PROMPT=1
       eval "$(pyenv init -)"
       eval "$(pyenv virtualenv-init -)"
       pyenv update
       pyenv install 3.7.2
       pyenv local 3.7.2
      
       # optional: run pyenv init in ~/.bashrc
       echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
       echo 'export PYENV_VIRTUALENV_DISABLE_PROMPT=1' >> ~/.bashrc
       echo 'eval "$(pyenv init -)"' >> ~/.bashrc
       echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
       
       # Create virtualenv for terms and conditions API 
       pyenv virtualenv 3.7.2 terms-cond-api
       
       # Show info
       pyenv versions
       pyenv virtualenvs
       # ls $HOME/.pyenv/versions/terms-cond-api/

       # Activate virtualenv
       pyenv activate terms-cond-api
       python3 --version
       pip3 install --upgrade pip
       
       # Setup demo terms and conditions API 
       cd ~
       git clone https://github.com/imec-ilabt/terms-cond-demo-site
       cd ~/terms-cond-demo-site/python_tc_api
       pip3 install -e .
       # ls "$HOME/.pyenv/versions/terms-cond-api/bin/"
       
       # Create DB
       FLASK_APP=tcapi.tc_api_app "$HOME/.pyenv/versions/terms-cond-api/bin/flask" init-db
       
       # Start the server
       FLASK_APP=tcapi.tc_api_app "$HOME/.pyenv/versions/terms-cond-api/bin/flask" run -p 8042

Note that for a production server, it is better to run the flask app through a tool as `gunicorn`. 
Running `flask` directly is meant for development servers only.
