#!/usr/bin/python3

# Batch add tags to HealthChecks.io checks
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 11-11-2022

import requests
import json

# HealthCheaks.io
healthChecks_API = "Your Healthchecks.io API key"
exclusiveTag = "unifi-cameras" # This tag should be exclusively used for these cameras
api_url = "https://healthchecks.io/api/v1/checks/"
headers = {"X-Api-Key": healthChecks_API}

def addTag(uuid,tags,new_tag):
    # Adds a check to an existing tag
    payload = {"tags":tags+" "+new_tag}
    r1 = requests.post(api_url+uuid, headers=headers, data=json.dumps(payload))
    return r1.status_code

# Get list of current checks with our camera tag
r = requests.get(api_url, headers=headers, params={"tag":exclusiveTag}).json()
checks = {}

# Strip out all information except for the actual camera name and the ping url.
for check in r["checks"]:
    checks[check["update_url"].split("/")[-1]] = {"name":check["name"],"tags":check["tags"].split(" ")}
    if check["name"] not in check["tags"].split(" "):
        r = addTag(uuid = check["update_url"].split("/")[-1],
                   tags = check["tags"],
                   new_tag = check["name"])
        print(check["name"],r)
    else:
        print(check["name"],"has tag already")