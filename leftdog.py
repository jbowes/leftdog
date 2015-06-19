# coding=utf-8

import base64
import json
import logging
import os
import sys

from datetime import datetime, timedelta

import falcon
import requests

log = logging.getLogger("leftdog")

AUTH_USERNAME = os.environ.get("AUTH_USERNAME")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")

DATADOG_API_KEY = os.environ.get("DATADOG_API_KEY")
DATADOG_APP_KEY = os.environ.get("DATADOG_APP_KEY")


class AuthMiddleware(object):

    def __init__(self):
        self.auth = base64.b64encode(AUTH_USERNAME + ":" + AUTH_PASSWORD)

    def process_request(self, req, resp):
        header = req.get_header("Authorization")

        if header is None:
            raise falcon.HTTPUnauthorized("Authorization required",
                    "Authorization header missing")

        if not self._auth_is_valid(header):
            raise falcon.HTTPUnauthorized("Invalid Authorization",
                    "Authorization header does not match")

    def _auth_is_valid(self, auth):
        auth_type, value = auth.split(" ")
        return auth_type.lower() == "basic" and value == self.auth

class ResponseLoggerMiddleware(object):

    def process_response(self, req, resp, resource):
        log.info('{0} {1} {2}'.format(req.method, req.relative_uri,
            resp.status[:3]))


class LeftdogResource:

    def on_get(self, req, resp, resp_type):
        units = req.params["units"]
        count = int(req.params.get("count", 1))
        query = req.params["q"]
        should_round = req.params.get("round", "false").lower() in ["true", "t"]
        op = req.params.get("op", "avg").lower()
        if op not in ["avg", "sum"]:
            resp.body=json.dumps({"error": "op must be one of avg or sum"})
            resp.status = falcon.HTTP_400
            return

        end = datetime.utcnow()
        start = end - timedelta(**{units: count})

        dd_resp = requests.get("https://app.datadoghq.com/api/v1/query",
            params={
            "api_key": DATADOG_API_KEY,
            "application_key": DATADOG_APP_KEY,
            "from": int(start.strftime("%s")),
            "to": int(end.strftime("%s")),
            "query": query,
            })

        log.info("DD response: %d", dd_resp.status_code)
        data = dd_resp.json()

        group_by = None
        if "group_by" in data and len(data["group_by"]) > 0:
            group_by = data["group_by"]

        if resp_type == "number":
            points = data["series"][0]["pointlist"]
            avg = sum([x[1] or 0 for x in points])
            if op == "avg":
                avg /= data["series"][0]["length"]
            if should_round:
                avg = round(avg)
            resp.body = json.dumps({"number": avg})
        elif resp_type == "pie":
            pie = {"chart": []}
            for series in data["series"]:
                scope = dict([x.split(":") for x in series["scope"].split(",")])
                name = " ".join([scope[x] for x in group_by])
                points = series["pointlist"]
                total = sum([x[1] or 0 for x in points])
                pie["chart"].append({
                    "name": name,
                    "value": int(total),
                    })

            resp.body = json.dumps(pie)

        resp.status = falcon.HTTP_200


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
    AuthMiddleware(),
    ResponseLoggerMiddleware(),
    ])
app.add_route("/v0/{resp_type}/", LeftdogResource())
