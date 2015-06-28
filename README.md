# Leftdog

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/jbowes/leftdog)

Leftdog is a translation layer to allow populating Leftronic widgets with
Datadog stats.

## Setup

1. Deploy Leftdog to Heroku (or elsewhere).
2. Configure the following:
  - `AUTH_USERNAME` A username you'll configure in Leftronic
  - `AUTH_PASSWORD` A password you'll configure in Leftronic
  - `DATADOG_API_KEY` One of your Datadog [API keys](https://app.datadoghq.com/account/settings#api)
  - `DATADOG_APP_KEY` One of your Datadog APP keys

## Usage

Set up a Leftronic 'My Custom Data' widget, set to 'Pull'.

Configure the url of the form:
```
https://<leftdog-url>/v0/number/?units=hours&q=<datadog-query>
```

Enjoy!
