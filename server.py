#!/usr/bin/python3

import flask
import json
import argparse
import os
import datetime
import subprocess

app = flask.Flask("Simple Web-Based Service Restarts")

def restart(service):
    if not service.endswith(".service"):
        service += ".service"
   
    process = subprocess.run(['sudo', '/bin/systemctl', 'restart', service], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    return (process.returncode, process.stdout, process.stderr)

@app.route('/', methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        return flask.render_template("overview.html", services=app.config["SYSTEMD_SERVICES"])
    elif flask.request.method == "POST":
        service = flask.request.form.get("service")
        if service and service in [ item["name"] for item in app.config["SYSTEMD_SERVICES"]]:
            retCode, stdout, stderr = restart(service)
            if retCode != 0:
                return (stdout.decode("UTF-8") + stderr.decode("UTF-8"), 500)
            else:
                return ("", 204)
        else:
            print(service, app.config["SYSTEMD_SERVICES"])
            return ("Missing or bad Service Parameter", 400)
    else:
        return ("Unsupported Method", 405)
        

@app.before_first_request
def init():
    with open("services.json") as f:
        config = json.load(f)
        app.config["SYSTEMD_SERVICES"] = config["systemd"]

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start Simple Web-based Service Restarts')
    parser.add_argument('--interface', default="localhost", help='Interface to run on')
    parser.add_argument('--port', default="5000", help='Port to run on')

    args = parser.parse_args()
    app.run(host=args.interface, port=args.port)
