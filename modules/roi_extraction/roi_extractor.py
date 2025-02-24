import cv2
import numpy as np

# type hinting
from cv2.typing import MatLike
Point = tuple[int, int]
Corners = tuple[Point, Point, Point, Point]


class ROIExtractor:
    def __init__(self, detector: cv2.aruco.ArucoDetector) -> None:
        self.arucodetector = detector

    def get_marker_locations(
            self,
            image: MatLike
            ) -> tuple[dict[int, Point], dict[int, Corners]]:
        marker_corners, marker_ids, _ = self.arucodetector.detectMarkers(image)
        centers: dict[int, Point] = {}
        corners: dict[int, Corners] = {}

        if marker_ids is None:
            raise ValueError('No markers found')

        for id_, corners_ in zip(marker_ids.flatten(), marker_corners):
            points = corners_.reshape((4, 2))
            center = np.mean(points, axis=0).astype(int)
            centers[id_] = tuple(center)
            corners[id_] = tuple([tuple(x.astype(int)) for x in points])

        return centers, corners

    def draw_markers(
            self,
            image: MatLike,
            centers: dict[int, Point],
            corners: dict[int, Corners]):
        for id_, center in centers.items():
            cv2.putText(
                img=image,
                text=f'{id_}',
                org=center,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.35,
                color=(0, 0, 255),
                thickness=1,
                lineType=cv2.LINE_AA
            )

        for id_, corner in corners.items():
            (tl, tr, br, bl) = corner
            cv2.line(image, tl, tr, (0, 0, 255), 2)
            cv2.line(image, tr, br, (0, 0, 255), 2)
            cv2.line(image, br, bl, (0, 0, 255), 2)
            cv2.line(image, bl, tl, (0, 0, 255), 2)

    def draw_roi(
            self,
            image: MatLike,
            locations: dict[int, tuple[int, int]],
            x1_id: int, x2_id: int, y1_id: int, y2_id: int) -> None:
        x1 = locations[x1_id][0]
        x2 = locations[x2_id][0]
        y1 = locations[y1_id][1]
        y2 = locations[y2_id][1]

        roi_tl = (x1, y1)
        roi_tr = (x2, y1)
        roi_br = (x2, y2)
        roi_bl = (x1, y2)

        cv2.line(image, roi_tl, roi_tr, (0, 255, 0), 2)
        cv2.line(image, roi_tr, roi_br, (0, 255, 0), 2)
        cv2.line(image, roi_br, roi_bl, (0, 255, 0), 2)
        cv2.line(image, roi_bl, roi_tl, (0, 255, 0), 2)

    def crop_roi(
            self,
            image: MatLike,
            locations: dict[int, tuple[int, int]],
            x1_id: int, x2_id: int, y1_id: int, y2_id: int) -> MatLike:
        x1 = locations[x1_id][0]
        x2 = locations[x2_id][0]
        y1 = locations[y1_id][1]
        y2 = locations[y2_id][1]

        return image[y1:y2, x1:x2].copy()

    def draw_roi_coordinates(
            self,
            image: MatLike,
            x1: int, y1: int, x2: int, y2: int):
        roi_tl = (x1, y1)
        roi_tr = (x2, y1)
        roi_br = (x2, y2)
        roi_bl = (x1, y2)
        cv2.line(image, roi_tl, roi_tr, (0, 255, 0), 2)
        cv2.line(image, roi_tr, roi_br, (0, 255, 0), 2)
        cv2.line(image, roi_br, roi_bl, (0, 255, 0), 2)
        cv2.line(image, roi_bl, roi_tl, (0, 255, 0), 2)

    def crop_roi_coordinates(
            self,
            image: MatLike,
            x1: int, y1: int, x2: int, y2: int):
        return image[y1:y2, x1:x2].copy()


def main():
    extractor = ROIExtractor()

    image = cv2.imread('./scanned/fiducial_test_6.png')
    centers, corners = extractor.get_marker_locations(image)
    centers = dict(sorted(centers.items()))
    corners = dict(sorted(corners.items()))
    for id_, coords in centers.items():
        print(f'{id_} : {coords}')

    extractor.draw_roi(image, centers, 200, 201, 300, 301)
    extractor.draw_roi(image, centers, 202, 203, 302, 303)
    extractor.draw_roi(image, centers, 204, 205, 303, 304)
    extractor.draw_roi(image, centers, 206, 207, 304, 305)
    extractor.draw_roi(image, centers, 208, 206, 305, 306)
    extractor.draw_roi(image, centers, 202, 203, 307, 308)
    extractor.draw_roi(image, centers, 204, 205, 308, 309)
    extractor.draw_roi(image, centers, 206, 209, 309, 310)
    extractor.draw_roi(image, centers, 210, 211, 309, 310)
    extractor.draw_roi(image, centers, 211, 201, 309, 310)
    extractor.draw_roi(image, centers, 208, 201, 311, 312)
    extractor.draw_roi(image, centers, 200, 201, 313, 314)
    extractor.draw_roi(image, centers, 214, 206, 314, 315)
    extractor.draw_roi(image, centers, 206, 215, 314, 315)
    extractor.draw_roi(image, centers, 212, 213, 314, 315)
    extractor.draw_roi(image, centers, 210, 201, 315, 316)

    extractor.draw_markers(image, centers, corners)

    cv2.imshow('Image', image)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
