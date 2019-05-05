MyCMS
=====
[![Ubuntu](https://img.shields.io/badge/ubuntu-18.04-purple.svg?style=flat-square)](http://releases.ubuntu.com/18.04/)
[![Python](https://img.shields.io/badge/python-3.6.7-orange.svg?style=flat-square)](https://www.python.org/downloads/release/python-367/)
[![Django](https://img.shields.io/badge/django-2.1.4-darkgreen.svg?style=flat-square)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/celery-4.2.1-green.svg?style=flat-square)](http://www.celeryproject.org/)
#### System for programming contests
+ Solutions run in a sandbox based on [isolate](https://github.com/ioi/isolate/tree/8cf2846206ac1573b4240afc98e08b67ae4d23f9)
+ Problems are uploaded from [Polygon](https://polygon.codeforces.com/) through its integrated [API](https://codeforces.com/blog/entry/45923?locale=en)


Installation
------------

### 1. Download the repository
Note that since we are using [isolate](https://github.com/ioi/isolate/tree/8cf2846206ac1573b4240afc98e08b67ae4d23f9) submodule you should add `--recursive` option to the regular cloning command
```bash
git clone --recursive https://github.com/Krauchman/mycms.git
```
Or, if you have already cloned the repository, just download the submodules by running
```bash
git submodule update --init
```
- - - -

### 2. Install the dependencies

#### 2.1. Python packages 
To install python packages with pip:
```bash
pip3 install -r requirements.txt
```
It is recommended to use a virtual environment, since we are using specific versions of python packages.

#### 2.2. RabbitMQ for Celery
We are using [RabbitMQ](https://www.rabbitmq.com/) as a task broker for Celery.

First, update your system:
```bash
sudo apt-get update
sudo apt-get upgrade
```
To install RabbitMQ on newer versions of Ubuntu (16.04, 18.04), run
```bash
apt-get install -y erlang
apt-get install rabbitmq-server
```
Next, enable and start `rabbitmq-server`:
```bash
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
```
Check the status to make sure everything works
```bash
systemctl status rabbitmq-server
```
- - - -

### 3. Configure isolate

#### 3.1. Build isolate binary
To build the isolate submodule run the following command from inside its directory
```bash
make isolate
```

#### 3.2. Configure environment
Run the following command to check some system settings
```bash
isolate-check-environment --execute
```
> If --execute is not specified, the recommended actions are written to stdout as an executable shell script, otherwise, using --execute will attempt to make changes to make the system behave more deterministically. The changes performed by --execute persist only until a reboot. To persist across reboots, the standard output from this script should be added to /etc/rc.local or some other script that is run on each boot.
- - - -

### 4. Migrate
Finally, do not forget to migrate
```bash
python3 manage.py migrate
```
- - - -

Starting the development (!) server
-------------------
To start the django development server
```bash
python3 manage.py runserver
```
You should also start a celery worker to run solutions and generate output for tests
```bash
celery -A mycms worker -l info
```
