#!/bin/bash

# Customise watermarks on Unifi cameras
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 26-10-2021
# update.sh <camera ip> <camera password>
# Tested on Unifi Video 3.10.13 and G2/G3 Unifi cameras
# Commands are sent over separate SSH connections because I didn't want to deal with chaining commands 

# Add the server key to known_hosts
sshpass -p $2 ssh -o "StrictHostKeyChecking=no" ubnt@$1 ls

# Upload a custom watermark
# Image should be a PNG no greater than 1024x1024. Black will be treated as transparent.
# The image uploaded to the camera must be labelled as user_logo for the camera to recognise it
sshpass -p $2 scp -v user_logo ubnt@$1:/etc/persistent

# Enable custom watermarks - The output from this line will be quite large
sshpass -p $2 ssh -o "StrictHostKeyChecking=no" ubnt@$1 "ubnt_ipc_cli -T=ubnt_osd -r=1 -m='{\"functionName\":\"ChangeOsdSettings\", \"useCustomLogo\":1}'"

# Set the logo scale [1-100%] - The output from this line will be quite large
sshpass -p $2 ssh -o "StrictHostKeyChecking=no" ubnt@$1 "ubnt_ipc_cli -T=ubnt_osd -r=1 -m='{\"functionName\":\"ChangeOsdSettings\", \"logoScale\":50}'"

# Write the configuration and file changes to the camera
sshpass -p $2 ssh -o "StrictHostKeyChecking=no" ubnt@$1 "cfgmtd -w -p /etc/"

# Reboot the camera, it's possible to restart the OSD service directly but this seems safer
sshpass -p $2 ssh -o "StrictHostKeyChecking=no" ubnt@$1 "reboot"
