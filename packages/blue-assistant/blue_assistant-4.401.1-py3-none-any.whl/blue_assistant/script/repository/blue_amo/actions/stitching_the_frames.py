from typing import List
import numpy as np
import cv2
from tqdm import trange
import math

from blueness import module
from blue_objects import file, objects
from blue_options import string

from blue_assistant import NAME
from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


def stitching_the_frames(
    script: BaseScript,
    node_name: str,
) -> bool:
    list_of_frames_filenames: List[str] = [
        filename
        for filename in [
            script.nodes[node_name_].get("filename", "")
            for node_name_ in [
                f"generating_frame_{index+1:03d}"
                for index in range(script.vars["frame_count"])
            ]
        ]
        if filename
    ]
    if not list_of_frames_filenames:
        return True

    logger.info(
        "{} frames to stitch: {}".format(
            len(list_of_frames_filenames),
            ", ".join(list_of_frames_filenames),
        )
    )

    list_of_frames: List[np.ndarray] = []
    for filename in list_of_frames_filenames:
        success, frame = file.load_image(
            objects.path_of(
                filename=filename,
                object_name=script.object_name,
            )
        )

        if success:
            list_of_frames += [frame]

    if not list_of_frames:
        return True

    common_height = list_of_frames[0].shape[0]
    common_width = list_of_frames[0].shape[1]
    for index in trange(1, len(list_of_frames)):
        frame_height = list_of_frames[index].shape[0]
        frame_width = list_of_frames[index].shape[1]

        if frame_height != common_height or frame_width != common_width:
            list_of_frames[index] = cv2.resize(
                list_of_frames[index],
                (common_width, common_height),
                interpolation=cv2.INTER_AREA,
            )

    width_count = int(math.ceil(math.sqrt(len(list_of_frames))))
    height_count = int(math.ceil(len(list_of_frames) / width_count))
    logger.info(
        "{} x {} -> {} x {}".format(
            len(list_of_frames),
            string.pretty_shape_of_matrix(list_of_frames[0]),
            height_count,
            width_count,
        )
    )

    list_of_frames += (height_count * width_count - len(list_of_frames)) * [
        np.zeros_like(list_of_frames[0])
    ]

    full_frame: np.ndarray = None
    for height_index in trange(height_count):
        row = np.concatenate(
            list_of_frames[
                height_index * width_count : (height_index + 1) * width_count
            ],
            axis=1,
        )

        if not height_index:
            full_frame = row
        else:
            full_frame = np.concatenate([full_frame, row], axis=0)
    logger.info(f"full frame: {string.pretty_shape_of_matrix(full_frame)}")

    for scale in [1, 2, 4]:
        scaled_full_frame = (
            full_frame
            if scale == 1
            else cv2.resize(
                full_frame,
                (
                    int(full_frame.shape[1] / scale),
                    int(full_frame.shape[0] / scale),
                ),
                interpolation=cv2.INTER_AREA,
            )
        )

        if not file.save_image(
            objects.path_of(
                filename="{}{}.png".format(
                    node_name,
                    "" if scale == 1 else f"-{scale}",
                ),
                object_name=script.object_name,
            ),
            scaled_full_frame,
            log=True,
        ):
            return False

    return True
