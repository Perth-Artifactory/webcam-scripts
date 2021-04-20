#!/usr/bin/python3

# Unifi Video snapshots via API
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 20-04-2021
# Tested on Unifi Video 3.10.13 

from unifi_video import UnifiVideoAPI
import time
import shutil

# Connect to the NVR. This API isn't supported on older versions of Unifi Video
uva = UnifiVideoAPI(api_key='Unifi Video API key', addr='nvr2',
    port=7443, schema='https', verify_cert=False)

# list the cameras that we want to pull and which should be pulled but disabled. Snapshot should be used for long term changes, disabled for short term disabling of a specific camera.
snapshot = ["lab","carpark","foyer","project","project2","band"]
disabled = []

# Iterate over currently online managed cameras
for camera in uva.active_cameras:
    if camera.name in snapshot and camera.name not in disabled:
        # This script is currently ran via watch so print statements are used as an activity indicator
        print(camera.name,time.time())
        camera.snapshot(filename="/var/www/webcams/{}.jpg".format(camera.name))
    elif camera.name in disabled:
        print(camera.name,time.time(),"DISABLED")
        # offline.jpg is a static image stating that the camera is offline or has been disabled
        shutil.copy("/var/www/webcams/offline.jpg","/var/www/webcams/{}.jpg".format(camera.name))
    else:
        # We have a number of cameras that are active but don't require snapshots
        print(camera.name,time.time(),"IGNORED")
