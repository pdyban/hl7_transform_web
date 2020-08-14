# HL7 Transform Web
![Build status](https://img.shields.io/github/workflow/status/pdyban/hl7_transform_web/CI)
![License](https://img.shields.io/github/license/pdyban/hl7_transform_web)
![Web service status](https://img.shields.io/website?down_message=offline&up_message=running&url=https%3A%2F%2Fdry-scrubland-17118.herokuapp.com%2F)

Flask-based web interface that allows to easily transform HL7v2 messages
using [hl7_transform](https://github.com/pdyban/hl7_transform) library.
Examples sections shows how to quickly start with creation and modification
of your own HL7v2 messages.

A running version of this web application running on a Heroku server can be
found here: https://dry-scrubland-17118.herokuapp.com/

# How to run
## Flask webserver
Create a new virtual environment and install the necessary prerequisites:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You can now run the app locally using flask's own built-in web server:
```sh
flask run
```
This version is **not recommended for deployment**, but is a convenient way to test
during development.

## Using gunicorn
You can run this application in gunicorn (in a Python virtual environment,
see above) in the following manner:
```sh
gunicorn app:app
```

## In Heroku
This repository is linked to a Heroku account and will update the running
instance code once the build has been successful. For a manual upgrade of the
Heroku application, push the local git master branch to heroku:
```sh
git push heroku master
```

# How to test
The test suite is implemented using Selenium, Chrome Webdriver and Pytest.
To run tests locally, make sure to install Google Chrome browser in version 84
and the respective Webdriver for your browser version and operating system.
Webdrivers for Chrome can be
downloaded [here](https://chromedriver.chromium.org/downloads).

Having the necessary dependencies, you can now test the application locally.
First, launch the local webserver (see above *How to run/Flask webserver*):
```sh
flask run --port 8000
```

Next, launch pytest in a separate virtual environment:
```sh
pytest
```
