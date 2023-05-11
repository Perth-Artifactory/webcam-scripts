#!/usr/bin/python3

# Get temp data from Home Assistant
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)

import requests
from pprint import pprint
import json

token = "Bearer TOKEN"

sensors = {"name": "entity_id",
           "second_name": "entity_id"}


url = "http://home.assistant:8123/api/states/"
headers = {
    "Authorization": token,
    "content-type": "application/json",
}

data = {}
for sensor in sensors:
    r = requests.get(url+sensors[sensor], headers=headers)
    t = r.json()["state"]
    data[sensor] = round(float(t),1)

print(json.dumps(data))
