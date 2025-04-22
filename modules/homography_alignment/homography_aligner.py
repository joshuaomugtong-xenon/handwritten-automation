import numpy as np
import cv2

type MatLike = cv2.typing.MatLike


class HomographyAligner:
    def __init__(self, detector: cv2.aruco.ArucoDetector) -> None:
        self.arucodetector = detector

    def align(
            self,
            image: MatLike,
            marker_image: MatLike,
            length=1700,
            width=2800
            ) -> MatLike:

        marker_corners, marker_ids, _ = self.arucodetector.detectMarkers(marker_image)

        if marker_ids is None:
            raise ValueError('No markers found')

        marker_ids = marker_ids.flatten()

        marker_dict = {}
        for i, id_ in enumerate(marker_ids):
            if id_ in [100, 101, 102, 103]:
                marker_dict[id_] = marker_corners[i][0]

        if len(marker_dict) < 4:
            raise ValueError(
                f"Found {len(marker_dict)} markers {' '.join(str(k) for k in marker_dict.keys())}. Not all markers found.")

        coords_markers = np.float32([
            marker_dict[100][0],  # top-left
            marker_dict[101][1],  # top-right
            marker_dict[103][2],  # bottom-right
            marker_dict[102][3],  # bottom-left
        ])

        coords_transform = np.float32([
            [0, 0],
            [length, 0],
            [length, width],
            [0, width],
        ])

        matrix = cv2.getPerspectiveTransform(coords_markers, coords_transform)
        aligned = cv2.warpPerspective(image, matrix, (length, width))

        return aligned
