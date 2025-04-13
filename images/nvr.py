import json
import asyncio
import logging
import time
from uiprotect import ProtectApiClient
import os
import shutil


class EpochTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return str(int(time.time()))


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
for handler in logging.getLogger().handlers:
    handler.setFormatter(EpochTimeFormatter("%(asctime)s [%(levelname)s] %(message)s"))

# Load config from file
with open("config.json", "r") as f:
    config: dict = json.load(f)
if not config["path"].endswith("/"):
    config["path"] += "/"

# Check for --all
if "--all" in os.sys.argv:
    config["cameras"]["ignored"] = []
    logging.info("Ignoring 'ignored' config")

protect = ProtectApiClient(
    host=config["nvr"]["host"],
    port=443,
    username=config["nvr"]["user"],
    password=config["nvr"]["password"],
    verify_ssl=False,
)

disabled = []


async def list_cameras():
    """List all cameras and update snapshots"""

    await protect.update()

    global disabled
    disabled = []
    for camera in protect.bootstrap.cameras.values():
        print(camera.name)
        if camera.name in config["cameras"]["ignored"]:
            logging.info(f"IGNORE {camera.name}")
            continue
        if camera.name in config["cameras"]["disabled"]:
            logging.info(f"DISABLED {camera.name}")
            shutil.copy("./images/offline.jpg", f"{config['path']}{camera.name}.jpg")
            disabled.append(camera.name)
            continue
        snapshot = await protect.get_camera_snapshot(camera.id)

        if snapshot:
            with open(f"{config['path']}{camera.name}.jpg", "wb") as f:
                logging.info(f"WRITING {camera.name}")
                f.write(snapshot)
        else:
            logging.info(f"FAILED {camera.name}")
            shutil.copy("./images/offline.jpg", f"{config['path']}{camera.name}.jpg")
            disabled.append(camera.name)


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
