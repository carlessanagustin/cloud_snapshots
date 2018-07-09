PYTHON_ENV=pyenv
PROG=gcp_snapshots

export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"

#cron
# * 2 * * * root source $WORKING_PATH/pyenv/bin/activate && python gcp_snapshots.py -v test-carles-mon-001 -s test-carles -c ./gcp_secrets.py -i 4 > /dev/null

install: logrotate virtualenv

test:
	sh -c ". ./pyenv/bin/activate && python gcp_snapshots.py -v test-carles-mon-001 -s test-carles -i 4"

env:
	sh -c 'source ${PYTHON_ENV}/bin/activate'

virtualenv:
	virtualenv ${PYTHON_ENV}
	${PYTHON_ENV}/bin/pip install -r requirements.txt

logrotate:
	sudo mkdir -p /var/log/${PROG}
	sudo chown -Rf $(shell whoami):$(shell whoami) /var/log/${PROG}
	sudo cp ./logrotate.conf /etc/logrotate.d/${PROG}

teardown:
	sudo rm -Rf /var/log/${PROG}
	sudo rm -Rf ${PYTHON_ENV}
	sudo rm -f /etc/logrotate.d/${PROG}

packages:
	sudo apt-get -y install python-setools python-pip python-virtualenv
