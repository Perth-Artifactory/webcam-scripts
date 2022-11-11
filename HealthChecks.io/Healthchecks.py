#!/usr/bin/python3

# Add, ping and fail HealthChecks.io checks for individual cameras.
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 27-10-2021
# --ping - Enabling pinging checks when a camera is online
# --create-check - Enable creation of checks for cameras not already on HealthChecks.io
# --signal-fail - Enable signalling an offline camera for checks that were already added to HealthChecks.io
# --force - Ping checks even if the check is disabled
# --auto - Equivalent to --ping --create-check --signal-fail --force
# Tested on Unifi Video 3.10.13

import requests
import json
from unifi_video import UnifiVideoAPI
import sys

# Unifi Video
nvr_host = "Your Unifi Video host or ip"
unifiVideo_API = "Your Unfii Video API key"

# HealthCheaks.io
healthChecks_API = "Your Healthchecks.io API key"
exclusiveTag = "unifi-cameras" # This tag should be exclusively used for these cameras
extraTags = "" # Any other tags you want to add to new checks, space separated
api_url = "https://healthchecks.io/api/v1/checks/"
headers = {"X-Api-Key": healthChecks_API}

def createCheck(name,ctag,xtag):
    # Create a new check with a check in time of 5 minutes and a 1 minute grace period.
    payload = {"name":"cam-"+name,
               "tags":" ".join([ctag, xtag, "cam-"+name]),
               "desc":"A Unifi camera - check automatically added",
               "timeout":300,
               "grace":60}
    r1 = requests.post(api_url, headers=headers, data=json.dumps(payload)).json()
    return r1["ping_url"]

# Check for --auto
if "--auto" in sys.argv:
    sys.argv = ["--ping", "--create-check", "--signal-fail", "--force"]

# Get list of current checks with our camera tag
r = requests.get(api_url, headers=headers, params={"tag":exclusiveTag}).json()
checks = {}
# Strip out all information except for the actual camera name and the ping url.
for check in r["checks"]:
    name = check["name"][4:]
    if "--force" in sys.argv:
        if check["status"] == "paused":
            print("Check for {} found but is disabled. Will ping/fail this check anyway.".format(name))
        checks[name] = check["ping_url"]
    else:
        if check["status"] != "paused":
            checks[name] = check["ping_url"]
        else:
            print("Check for {} found but is disabled. Use --force to interact with this check.".format(name))

# get a list of cameras from the NVR
uva = UnifiVideoAPI(api_key=unifiVideo_API, addr=nvr_host,
    port=7443, schema='https', verify_cert=False)

# Iterate over currently online managed cameras
x = 0
for camera in uva.active_cameras:
    if camera.name in checks.keys():
        if "--ping" in sys.argv:
            requests.get(checks[camera.name], timeout=10)
            print("Check for {} found. Pinged".format(camera.name))
        else:
            print("Check for {} found. Use --ping to signal that the camera is online".format(camera.name))
        # Delete the check regardless of --ping
        del checks[camera.name]
    else:
        if "--create-check" in sys.argv:
            u = createCheck(camera.name,exclusiveTag,extraTags)

            # We can't ping a check that doesn't exist, hence the nest
            if "--ping" in sys.argv:
                requests.get(u, timeout=10)
                print("Check for {} not found. Created and pinged".format(camera.name))
            else:
                print("Check for {} not found. Created but not pinged. Use --ping to signal that the camera is online.".format(camera.name))
        else:
            print("Check for {} not found. Use --create-check to add a new check.".format(camera.name))


# Signal failures for checks that didn't have a matching camera

for check in checks:
    if "--signal-fail" in sys.argv:
        print("{} is listed as a check but the camera is offline. Signalling a failure".format(check))
        # Failure is triggered by appending /fail to the check url
        requests.get(checks[check]+"/fail", timeout=10)
    else:
        print("{} is listed as a check but the camera is offline. Use --signail-fail to signal a failure".format(check))
