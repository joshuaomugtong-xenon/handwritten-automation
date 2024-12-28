import numpy as np
import cv2

from cv2.typing import MatLike


class HomographyAligner:
    def __init__(self, detector: cv2.aruco.ArucoDetector) -> None:
        self.arucodetector = detector

    def align(
            self,
            image: cv2.typing.MatLike,
            length=1700,
            width=2200
            ) -> MatLike:

        marker_corners, marker_ids, _ = self.arucodetector.detectMarkers(image)

        if marker_ids is None:
            raise ValueError('No markers found')

        centers = []
        corners = []

        marker_dict = {
            id_: corners_.reshape((4, 2))
            for id_, corners_ in zip(marker_ids.flatten(), marker_corners)
            if id_ in [100, 101, 102, 103]
        }

        if len(marker_dict) < 4:
            raise ValueError('Not all markers found')

        for id_ in [100, 101, 102, 103]:
            points = marker_dict[id_]
            center = np.mean(points, axis=0)
            centers.append(center)
            corners.append(points)

        centers = np.array(centers)
        corners = np.array(corners)

        # Ideally, 100 top-left, 101 top-right, 102 bot-left, 103 bot-right

        # Find top-left: marker with smallest sum of x and y
        tl_idx = np.argmin(np.sum(centers, axis=1))

        # Find bottom-right: marker with largest sum of x and y
        br_idx = np.argmax(np.sum(centers, axis=1))

        # For remaining two points
        remaining_idx = [i for i in range(4) if i not in [tl_idx, br_idx]]
        p1, p2 = centers[remaining_idx]

        # Top-right will have larger x, smaller y
        if p1[0] > p2[0]:
            tr_idx = remaining_idx[0]
            bl_idx = remaining_idx[1]
        else:
            tr_idx = remaining_idx[1]
            bl_idx = remaining_idx[0]

        # Create the corner points
        tl = corners[tl_idx][0]
        tr = corners[tr_idx][1]
        br = corners[br_idx][2]
        bl = corners[bl_idx][3]
        coords_markers = np.float32([tl, tr, br, bl])
        coords_transform = np.float32(
            [[0, 0], [length, 0], [length, width], [0, width]])
        matrix = cv2.getPerspectiveTransform(coords_markers, coords_transform)
        aligned = cv2.warpPerspective(image, matrix, (length, width))

        return aligned
