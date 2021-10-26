#!/usr/bin/python3

# Unifi Video snapshots via anon snapshot endpoint
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 20-04-2021
# Tested on Ubiquiti Aircam, should also work on any Ubiquiti camera with the snapshot endpoint enabled
# This script utilises an anonymous mode that is automatically enabled on older cameras but needs to be explicitley enabled on newer cameras.
# The introduction of an API in later versions of Unifi Video render this obselete if you have priveldged access to the NVR

import requests
import shutil
import time

# list the cameras that we want to pull and which should be pulled but disabled. Cams should be used for long term changes, disable for short term disabling of a specific camera.
cams = ["activities", "lasers"]
disable = []

for cam in cams:
    if cam in disable:
        # offline.jpg is a static image stating that the camera is offline or has been disabled
        shutil.copy("/var/www/webcams/offline.jpg","/var/www/webcams/{}.jpg".format(cam))
    else:
        try:
            # This request relies on hostnames set by DHCP server 
            # The format doesn't match the hostnames that Unifi cameras will set for themselves
            r = requests.get("http://cam-{}/snapshot.cgi".format(cam), allow_redirects=True)
            open("/var/www/webcams/{}.jpg".format(cam), 'wb').write(r.content)
            print(time.time(),cam)
        except:
            # We don't really care why the pull failed, only that it did
            shutil.copy("/var/www/webcams/offline.jpg","/var/www/webcams/{}.jpg".format(cam))
            print(time.time(),cam," - Failed!")
