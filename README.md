# MyCMS
[![Python](https://img.shields.io/badge/python-3.6.7-orange.svg?style=flat-square)](https://www.python.org/downloads/release/python-367/)
[![Django](https://img.shields.io/badge/django-2.1.4-darkgreen.svg?style=flat-square)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/celery-4.2.1-green.svg?style=flat-square)](http://www.celeryproject.org/)
#### System for programming contests
+ Runs solutions in sandbox based on [isolate](https://github.com/ioi/isolate/tree/8cf2846206ac1573b4240afc98e08b67ae4d23f9)
+ Upload problems from [Polygon](https://polygon.codeforces.com/) through its integrated [API](https://codeforces.com/blog/entry/45923?locale=en)

## Installation
Note that since we are using [isolate](https://github.com/ioi/isolate/tree/8cf2846206ac1573b4240afc98e08b67ae4d23f9) submodule you should add `--recursive` option to the regular cloning command
```bash
git clone --recursive https://github.com/Krauchman/mycms.git
```
Or, if you have already cloned the repository, just download the submodules by running
```bash
git submodule update --init
```
