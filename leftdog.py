# coding=utf-8

import json
import logging
import os
import sys

from datetime import datetime

import falcon
import requests

log = logging.getLogger("leftdog")

AUTH_USERNAME = os.environ.get("AUTH_USERNAME")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")

DATADOG_API_KEY = os.environ.get("DATADOG_API_KEY")
DATADOG_APP_KEY = os.environ.get("DATADOG_APP_KEY")


class ResponseLoggerMiddleware(object):

    def process_response(self, req, resp, resource):
        log.info('{0} {1} {2}'.format(req.method, req.relative_uri,
            resp.status[:3]))


class LeftdogResource:

    def on_get(self, req, resp):
        resp = falcon.HTTP_200


def configure():
    if not AUTH_USERNAME:
        log.error("Please set AUTH_USERNAME")
        sys.exit(-1)
    if not AUTH_PASSWORD:
        log.error("Please set AUTH_PASSWORD")
        sys.exit(-1)
    if not DATADOG_API_KEY:
        log.error("Please set DATADOG_API_KEY")
        sys.exit(-1)
    if not DATADOG_APP_KEY:
        log.error("Please set DATADOG_APP_KEY")
        sys.exit(-1)


logging.basicConfig()
log.setLevel(logging.INFO)

configure()

app = falcon.API(middleware=[
    ResponseLoggerMiddleware(),
    ])
app.add_route("/", LeftdogResource())
