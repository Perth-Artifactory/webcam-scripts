#!/usr/bin/python3

# Presence detection / Named WiFi client summary
# Fletcher Boyd (fletcher.boyd@artifactory.org.au)
# Last modified: 20-04-2021
# Tested on Unifi Controller 5.x, 6.x
# jank af

from pyunifi.controller import Controller

# Initiate a connection to the controller, we use a self hosted certificate and trust the connection between this script's location and the controller.
c = Controller('IP', 'USER', 'PASS',ssl_verify=False)

# Define badges, these are matched against the notes field within the controller
images = {"committee": ['<img src="./images/artifactory.png" height="16" width="16" title="Committee Member">',"Committee Member"],
          "lasertrain": ['<img src="./images/lasertrain.png" height="16" width="16" title="Laser Trainer">',"Laser Trainer"],
          "laserfix": ['<img src="./images/laserfix.png" height="16" width="16" title="Laser Maintainer">',"Laser Maintainer"],
          "swarf": ['<img src="./images/swarf.png" height="16" width="16" title="CNC Router Trainer">',"CNC Router Trainer"],
          "guide": ['<img src="./images/smile.png" height="16" width="16" title="Gives tours">',"Gives Tours"],
          "electronics": ['<img src="./images/lightning.png" height="16" width="16" title="Electronics Experience">',"Electronics Experience"],
          "key": ['<img src="./images/key.png" height="16" width="16" title="24/7 Keyholder">',"24/7 Keyholder"],
          "3d": ['<img src="./images/3d.png" height="16" width="16" title="3D Printing Experience">',"3D Printing Experience"]}


# A list of Name/Slack ID pairs used for deep linking to a slack private message
slack = {"USER":"UXXXXXXXX"}

teamurl = "<a href='slack://user?team=TXXXXXXXX&id={}' target='_blank' title='Open a private message with {} on Slack'>{}</a>"

people = {}

# Iterate over clients
for ap in c.get_clients():
    # Only list people that have specifically opted in (designated by them having a custom name set)
    if "name" in ap.keys():
        # People can appear without any badges
        people[ap["name"]] = " "
        if "note" in ap.keys():
            people[ap["name"]] = ap["note"]
            for x in images:
                # Iterate over badges and sub in images
                people[ap["name"]] = people[ap["name"]].replace(x,images[x][0])

# Sort the list alphabetically so it's clear why someone is always listed first etc
li = list(people.keys())
li.sort()

# Sometimes the space is empty
if len(li) < 1:
    li = ["no one :("]
    people["no one :("] = " "

# start constructing a HTML block
s = "<ul>\n"

# iterate over the sorted list of people
for x in li:
    # add badges if they've got them
    if people[x] != " ":
        s = s+"<li>"+x+" "+people[x]+"</li>\n"
    else:
        s = s+"<li>"+x+"</li>\n"

# close out the list
s += "</ul><br>"

# generate a badge key
for image in images:
    s += "{} {} | ".format(images[image][0],images[image][1])
s = s[:-2]

# sub in slack deep linking
for x in slack:
    s = s.replace(x,teamurl.format(slack[x],x,x))

# write the file ready for inclusion in a larger page
with open('/var/www/webcams/people.html','w') as f:
    f.write(s)
