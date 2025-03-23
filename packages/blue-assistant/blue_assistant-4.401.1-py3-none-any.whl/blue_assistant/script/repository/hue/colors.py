from typing import List
import numpy as np
import cv2


# https://chatgpt.com/c/67d4c06c-2168-8005-9d8b-4b6c9848957e
def get_hue_values(
    colormap: int = cv2.COLORMAP_HOT,
    length: int = 255,
) -> List[int]:
    # Create a gradient from 0 to 255
    gradient = np.linspace(0, 255, length).astype("uint8")
    gradient = np.repeat(gradient[np.newaxis, :], 1, axis=0)

    # Apply the colormap
    color_mapped_image = cv2.applyColorMap(gradient, colormap)

    # Convert BGR to HSV
    hsv_image = cv2.cvtColor(color_mapped_image, cv2.COLOR_BGR2HSV)

    return (hsv_image[0, :, 0] * (65535 / 179)).astype(int).tolist()
