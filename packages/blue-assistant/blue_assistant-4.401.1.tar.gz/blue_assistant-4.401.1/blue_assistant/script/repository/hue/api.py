from typing import Tuple, Dict, List
import requests
from time import sleep
from tqdm import tqdm
import cv2
import random

from blueness import module

from blue_assistant import NAME
from blue_assistant import env
from blue_assistant.script.repository.hue.colors import get_hue_values
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


# hue-2025-03-14-1l8tv6
def create_user(
    bridge_ip: str = env.HUE_BRIDGE_IP_ADDRESS,
    wait_for_link_press: bool = True,
) -> str:
    URL = f"http://{bridge_ip}/api"

    payload = {
        "devicetype": "my_hue_app#python_script",
    }

    if wait_for_link_press:
        input("Press the link button on the Hue Bridge ...")

    try:
        response = requests.post(URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            if "success" in result[0]:
                username = result[0]["success"]["username"]
                logger.info(f"created {username}")
                return username

            logger.error(result)
            return ""

        logger.error(response)
        return ""
    except Exception as e:
        logger.error(e)
        return ""


# hue-2025-03-14-4r9mgh
def list_lights(
    bridge_ip: str = env.HUE_BRIDGE_IP_ADDRESS,
    username: str = env.HUE_BRIDGE_USERNAME,
    verbose: bool = False,
) -> Tuple[bool, Dict]:
    URL = f"http://{bridge_ip}/api/{username}"

    response = requests.get(URL)

    if response.status_code != 200:
        logger.error(response)
        return False, {}

    list_of_lights = response.json()["lights"]
    logger.info(
        "found {} light(s): {}".format(
            len(list_of_lights),
            ", ".join(list_of_lights.keys()),
        )
    )
    if verbose:
        for light_id, light_info in list_of_lights.items():
            logger.info(f"#{light_id}: {light_info}")

    return True, list_of_lights


# hue-2025-03-13-1xjr1z
def set_light_color(
    light_id: str,
    hue: int,  # 0 to 65535
    saturation: int,  # 0 to 254
    bridge_ip: str = env.HUE_BRIDGE_IP_ADDRESS,
    username: str = env.HUE_BRIDGE_USERNAME,
    verbose: bool = False,
) -> bool:
    logger.info(
        "{}.set_light_color({}@{}:{}) -> hue=0x{:x}, saturation=0x{:x}".format(
            NAME,
            username,
            bridge_ip,
            light_id,
            hue,
            saturation,
        )
    )

    # Construct the API endpoint URL
    url = f"http://{bridge_ip}/api/{username}/lights/{light_id}/state"

    # Prepare the payload with the desired hue and saturation
    payload = {
        "hue": hue,
        "sat": saturation,
    }

    response = requests.put(url, json=payload)

    # https://chat.openai.com/c/6deb94d0-826a-48de-b5ef-f7d8da416c82
    # response.raise_for_status()
    if response.status_code // 100 != 2:
        logger.error(response)
        return False

    if verbose:
        logger.info(response.json())

    return True


def test(
    colormap: int = cv2.COLORMAP_HOT,
    light_id: str = "all",
    interval: float = env.HUE_TEST_DEFAULT_INTERVAL,
    bridge_ip: str = env.HUE_BRIDGE_IP_ADDRESS,
    username: str = env.HUE_BRIDGE_USERNAME,
    verbose: bool = False,
) -> bool:
    if not light_id:
        light_id = "all"

    logger.info(
        "{}.test({}@{}:{}) @ colormap #{}, interval={} s".format(
            NAME,
            username,
            bridge_ip,
            light_id,
            colormap,
            interval,
        )
    )

    list_of_lights: List[str]
    if light_id == "all":
        success, dict_of_lights = list_lights(
            bridge_ip=bridge_ip,
            username=username,
            verbose=verbose,
        )
        if not success:
            return success
        list_of_lights = list(dict_of_lights.keys())
    else:
        list_of_lights = [light_id]

    list_of_hue_values = get_hue_values(
        colormap=colormap,
        length=len(list_of_lights),
    )
    list_of_hue_values = list_of_hue_values + list_of_hue_values

    hue_offset: int = 0
    try:
        while True:
            logger.info(f"hue_offset={hue_offset}")

            for light_index in tqdm(range(len(list_of_lights))):
                set_light_color(
                    light_id=list_of_lights[light_index],
                    hue=list_of_hue_values[hue_offset + light_index],
                    saturation=random.randint(1, env.HUE_MAX_SATURATION),
                    bridge_ip=bridge_ip,
                    username=username,
                    verbose=verbose,
                )

                sleep(interval)

            hue_offset = (hue_offset + 1) % len(list_of_lights)

    except KeyboardInterrupt:
        logger.info("Ctrl+C detected.")

    return True
