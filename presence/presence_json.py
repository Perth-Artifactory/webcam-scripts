#!/usr/bin/python3

# Presence detection / Named WiFi client summary
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 20-04-2021
# Tested on Unifi Controller 5.x, 6.x

from pyunifi.controller import Controller
import json

# Initiate a connection to the controller, we use a self hosted certificate and trust the connection between this script's location and the controller.
c = Controller('IP', 'USER', 'PASS',ssl_verify=False)

# A list of Name/Slack ID pairs used for deep linking to a slack private message
slack = {"USER":"UXXXXXXXX"}

people = {}

# Iterate over clients
for ap in c.get_clients():
    # Only list people that have specifically opted in (designated by them having a custom name set)
    if "name" in ap.keys():
        people[ap["name"]] = {"groups":[], "slack":""}
        # check for badges
        if "note" in ap.keys():
            people[ap["name"]]["groups"] = ap["note"].split(" ")
        # check for an associated slack account
        if ap["name"] in slack.keys():
            people[ap["name"]]["slack"] = slack[ap["name"]]

# dump the data
with open('/var/www/webcams/people.json', 'w') as o:
    json.dump(people, o)
