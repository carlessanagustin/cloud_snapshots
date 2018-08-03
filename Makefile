PYTHON_ENV=pyenv
PROG=cloud_snapshots
LC_ALL="en_US.UTF-8"
LC_CTYPE="en_US.UTF-8"

#cron
# * 2 * * * root source $WORKING_PATH/pyenv/bin/activate && python gcp_snapshots.py -v test-carles-mon-001 -s test-carles -c ./gcp_secrets.py -i 4 > /dev/null

install: logrotate virtualenv

uninstall:
	sudo rm -Rf /var/log/${PROG}
	sudo rm -Rf ${PYTHON_ENV}
	sudo rm -f /etc/logrotate.d/${PROG}


logrotate:
	sudo mkdir -p /var/log/${PROG}
	sudo chown -Rf $(shell whoami):$(shell whoami) /var/log/${PROG}
	sudo cp ./logrotate.conf /etc/logrotate.d/${PROG}

virtualenv:
	virtualenv -p python3 ${PYTHON_ENV}
	${PYTHON_ENV}/bin/pip3 install -r requirements.txt


packages:
	sudo apt-get update
	sudo apt-get -y install python-setools python3-pip python3-virtualenv
	
env:
	sh -c 'source ${PYTHON_ENV}/bin/activate'
