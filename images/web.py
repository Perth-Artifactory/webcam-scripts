import asyncio
import json
import logging
import os
import shutil
import time

from uiprotect import ProtectApiClient


class EpochTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return str(int(time.time()))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
for handler in logging.getLogger().handlers:
    handler.setFormatter(EpochTimeFormatter('%(asctime)s [%(levelname)s] %(message)s'))

# Load config from file
with open("config.json", "r") as f:
    config: dict = json.load(f)
if not config["path"].endswith("/"):
    config["path"] += "/"
    
# Check for --all
if "--all" in os.sys.argv:
    config["cameras"]["ignored"] = []
    logging.info("Forcing all ignored cameras to be included")

protect = ProtectApiClient(
    host=config["nvr"]["host"],
    port=443,
    username=config["nvr"]["user"],
    password=config["nvr"]["password"],
    verify_ssl=False,
)

disabled = []
snapshotted = []

async def list_cameras():
    """List all cameras and update snapshots"""
    
    await protect.update()

    global disabled
    disabled = []
    for camera in protect.bootstrap.cameras.values():
        if camera.name in config["cameras"]["ignored"]:
            logging.info(f"IGNORE {camera.name}")
            continue
        if camera.name in config["cameras"]["disabled"]:
            logging.info(f"DISABLED {camera.name}")
            shutil.copy("./images/offline.jpg", f"{config['path']}{camera.name}.jpg")
            disabled.append(camera.name)
            continue
        snapshot = await protect.get_camera_snapshot(camera.id)
        with open(f"{config['path']}{camera.name}.jpg", "wb") as f:
            logging.info(f"WRITING {camera.name}")
            snapshotted.append(camera.name)
            f.write(snapshot)
            
async def close():
    await protect.async_disconnect_ws()
    await protect._session.close()
    
asyncio.run(list_cameras())

for camera in config["cameras"]["disabled"]:
    if camera not in disabled:
        logging.info(f"O-DISABLED: {camera}")
        shutil.copy("./images/offline.jpg", f"{config['path']}{camera}.jpg")

# Close the connection
asyncio.run(close())




def ins(html,im):
    return html.format(im)

snapshotted.sort()
s = ""
count = 1
for image in snapshotted:
    s += f"""\n<div class="col"><a href="{image}.jpg" target="_blank"><img src="./{image}.jpg" class="img-fluid"></a></div>"""
    if count%3 == 0:
        s += """\n<div class="w-100"></div>"""
    count += 1
html = """
<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.2.1/dist/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous">

    <!-- Refresh page -->
    <meta http-equiv="refresh" content="10">
    <title>All cams</title>
  </head>
  <body style="background-color:black;">
    <div class="container-fluid">
        <div class="row ">
        {}
        </div>
      </div>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.6/dist/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.2.1/dist/js/bootstrap.min.js" integrity="sha384-B0UglyR+jN6CkvvICOB2joaf5I4l3gm9GU6Hc1og6Ls7i6U/mkkaduKaBhlAXv9k" crossorigin="anonymous"></script>
  </body>
</html>
"""

with open(f"{config['path']}index.html","w") as f:
    f.write(ins(html,s))