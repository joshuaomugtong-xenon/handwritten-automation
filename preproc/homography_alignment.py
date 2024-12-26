import numpy as np
import cv2
from cv2.typing import MatLike


def homography_alignment(
        image: MatLike,
        coords: np.ndarray,
        length=1700, width=2200
        ) -> MatLike:

    corners = np.float32([[0, 0], [length, 0], [length, width], [0, width]])
    matrix = cv2.getPerspectiveTransform(coords, corners)
    aligned = cv2.warpPerspective(image, matrix, (length, width))

    return aligned
