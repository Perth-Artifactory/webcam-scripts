#!/usr/bin/python3

# Bulk change Unifi camera settings
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 26-10-2021
# Tested on Unifi Video 3.10.13

from unifi_video import UnifiVideoAPI
import time
import shutil
import os

nvr = "NVR host"
api = "Unifi Video API key"
campass = "Camera password"

# Connect to the NVR. This API isn't supported on older versions of Unifi Video
uva = UnifiVideoAPI(api_key=api, addr=nvr,
    port=7443, schema='https', verify_cert=False)

# Iterate over currently online managed cameras 
for camera in uva.active_cameras:
    ip = camera._data['internalHost']
    # Run a series commands for each camera
    os.system("./update.sh {} {}".format(ip,campass))
