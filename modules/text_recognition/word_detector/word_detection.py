from math import pi
from typing import NamedTuple
from collections import defaultdict

import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN


class BBox(NamedTuple):
    x: int
    y: int
    w: int
    h: int

    def pad(self, padding: int) -> 'BBox':
        return BBox(
            self.x - padding,
            self.y - padding,
            self.w + 2 * padding,
            self.h + 2 * padding
        )

    def clamp(self, max_width: int, max_height: int) -> 'BBox':
        return BBox(
            _clamp(self.x, 0, max_width - 1),
            _clamp(self.y, 0, max_height - 1),
            _clamp(self.w, 0, max_width-self.x),
            _clamp(self.h, 0, max_height-self.y),
        )

    def area(self) -> int:
        return self.w * self.h

    def corners(self) -> np.ndarray:
        return np.array([
            self.top_left(),
            self.top_right(),
            self.bottom_right(),
            self.bottom_left()
        ])

    def crop(self, image: np.ndarray) -> np.ndarray:
        return image[self.y:self.y+self.h, self.x:self.x+self.w]

    def top_left(self) -> np.ndarray:
        return np.array([self.x, self.y])

    def bottom_right(self) -> np.ndarray:
        return np.array([self.x + self.w, self.y + self.h])

    def bottom_left(self) -> np.ndarray:
        return np.array([self.x, self.y + self.h])

    def top_right(self) -> np.ndarray:
        return np.array([self.x + self.w, self.y])


def _clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min(value, max_value), min_value)


def show_image(image: np.ndarray, title: str = 'Image') -> None:
    enabled = False
    if not enabled:
        return
    figure = plt.figure()
    ax = figure.add_subplot(1, 1, 1)
    ax.set_title(title)
    if image.ndim == 2:
        ax.imshow(image, cmap='gray')
    else:
        ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.set_aspect('equal')
    figure.tight_layout()
    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.showMaximized()


class WordDetector:
    """Word detection using scale space technique for word segmentation
    proposed by R. Manmatha.

    Source: http://ciir.cs.umass.edu/pubfiles/mm-27.pdf.
    """
    def __init__(
            self,
            kernel_size: int = 25,
            sigma: float = 15.0,
            theta: float = 7.0,
            dilation: int = 2,
            min_area: int = 100,
            line_px: int = 15,
            border_px: int = 10,
            padding_px: int = 5,
            ):

        self.kernel = _compute_kernel(kernel_size, sigma, theta)
        self.min_area = min_area
        self.dilation = dilation
        self.line_px = line_px
        self.border_px = border_px
        self.padding_px = padding_px

    def extract_words(
            self,
            image: np.ndarray
            ) -> list[BBox]:

        # Check input image if it is a color image
        assert image.ndim == 3
        assert image.dtype == np.uint8

        # Create a copy of the image for display purposes
        disp_image = image.copy()

        # Convert image to grayscale
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        show_image(image, 'Gray Image')

        image_gray = image.copy()

        # Threshold the image
        _, image = cv2.threshold(
            image, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        show_image(image, 'Thresholded Image')

        image_thresh = image.copy()

        # Isolate the border region
        h, w = image.shape
        b = self.border_px
        mask = np.zeros_like(image)
        mask[:b, :] = 255
        mask[-b:, :] = 255
        mask[:, :b] = 255
        mask[:, -b:] = 255
        border = cv2.bitwise_and(image, mask)
        show_image(border, 'Border Region')

        # Remove the horizontal and vertical lines from the border
        k = self.line_px
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, 1))
        h_lines = cv2.morphologyEx(border, cv2.MORPH_CLOSE, h_kernel)
        show_image(h_lines, 'Horizontal Lines')
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, k))
        v_lines = cv2.morphologyEx(border, cv2.MORPH_CLOSE, v_kernel)
        show_image(v_lines, 'Vertical Lines')
        mask = cv2.bitwise_or(h_lines, v_lines)
        show_image(mask, 'Removed Lines From Border')

        # Note: If the mask used is the entire border region, the inpainting
        # process will spill any connected words wider and into the ends of
        # the image (making the contour larger).
        # Using a mask made from the lines is preferrable so the inpainting is
        # localized and minimal.

        # Inpaint the image to remove the lines
        image = cv2.inpaint(image_thresh, mask, 3, cv2.INPAINT_TELEA)
        show_image(image, 'Removed Lines Image')

        # Dilate the image
        df = self.dilation
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (df, df))
        image = cv2.dilate(image, kernel, iterations=1)
        show_image(image, 'Dilated Image')

        # Apply the filter kernel
        image = cv2.filter2D(
            image, -1, self.kernel, borderType=cv2.BORDER_REPLICATE)
        image = image.astype(np.uint8)
        show_image(image, 'Filtered Image')

        # Threshold the image again
        _, image = cv2.threshold(
            image, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        show_image(image, 'Thresholded Image 2')

        # Find the contours in the binary image
        # cv2.RETR_EXTERNAL retrieves only the outer contours in case of nested
        contours = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Note: Isolating the word image using the contour as the mask tends to
        # leave out letters such as 'C' if its in the beginning of the word.
        # This is due to the filter kernel used, otherwise it does a great job
        # of isolating the word.
        # - Could be fixed by dilating the mask

        # Extract bounding boxes of the contours
        bboxes: list[BBox] = []
        for contour in contours:
            # Get bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)
            bbox = BBox(x, y, w, h)
            # Skip small bounding boxes
            if bbox.area() < self.min_area:
                continue
            # pad the bounding box
            bbox = bbox.pad(self.padding_px)
            bbox = bbox.clamp(image.shape[1], image.shape[0])
            cv2.rectangle(
                disp_image,
                bbox.top_left()-1, bbox.bottom_right()-1,
                (0, 255, 0), 1)
            bboxes.append(bbox)
            word_image = bbox.crop(image_gray)
            # Compute the weighted centroid of the word image
            a, b = _compute_weighted_centroid(word_image)
            # Draw the centroid on the display image
            disp_image[bbox.y + b, bbox.x + a] = [255, 0, 0]

        show_image(disp_image, 'Detected Words')

        plt.show()

        if bboxes:
            return sort_multiline(bboxes)
        else:
            return []


def _compute_weighted_centroid(image: np.ndarray) -> tuple[int, int]:
    """Compute the weighted centroid of a binary image.

    ### Args:
        `image`: A grayscale image.

    ### Returns:
        A tuple containing the x and y coordinates of the weighted centroid.
    """

    assert image.ndim == 2
    assert image.dtype == np.uint8

    # Compute the total sum of the image
    total = np.sum(image)

    # Compute the x and y coordinates of the weighted centroid
    y, x = np.indices(image.shape)
    a: np.float64 = np.sum(image * x) / total
    b: np.float64 = np.sum(image * y) / total

    a, b = int(a.round()), int(b.round())

    return a, b


def _compute_kernel(
        kernel_size: int,
        sigma: float,
        theta: float,
        ) -> np.ndarray:
    """Compute anisotropic filter kernel.

    ### Args:
        `kernel_size`: The size of the filter kernel, must be an odd integer.
        `sigma`: Standard deviation of Gaussian function used for filter
        kernel.
        `theta`: Approximated width/height ratio of words, filter function is
        distorted by this factor.

    ### Returns:
        An anisotropic filter kernel.
    """

    # Kernel size must be odd
    assert kernel_size % 2

    # Create coordinate grid
    half_size = kernel_size // 2
    xs = ys = np.linspace(-half_size, half_size, kernel_size)
    x, y = np.meshgrid(xs, ys)

    # Compute sigma values in x and y direction, where theta is roughly the
    # average x/y ratio of words
    sigma_y = sigma
    sigma_x = sigma_y * theta

    # Compute terms and combine them
    exp_term = np.exp(-x ** 2 / (2 * sigma_x) - y ** 2 / (2 * sigma_y))
    x_term = (x ** 2 - sigma_x ** 2) / (2 * pi * sigma_x ** 5 * sigma_y)
    y_term = (y ** 2 - sigma_y ** 2) / (2 * pi * sigma_y ** 5 * sigma_x)
    kernel = (x_term + y_term) * exp_term

    # Normalize the kernel
    kernel = kernel / np.sum(kernel)

    return kernel


def _cluster_lines(
        bboxes: list[BBox],
        max_dist: float = 0.7,
        min_words_per_line: int = 1
        ) -> list[list[BBox]]:
    """Cluster detections into lines using DBSCAN algorithm.

    ### Args:
        `bboxes`: List of bounding boxes.
        `max_dist`: Maximum Jaccard distance (0..1) between two y-projected
        words to be considered as neighbors.
        `min_words_per_line`: If a line contains less words than specified, it
        is ignored.

    ### Returns:
        List of lines, with each line corresponding to a list of bboxes.
    """

    num_bboxes = len(bboxes)
    dist_mat = np.ones((num_bboxes, num_bboxes))
    for i in range(num_bboxes):
        for j in range(i, num_bboxes):
            a = bboxes[i]
            b = bboxes[j]
            if a.y > b.y + b.h or b.y > a.y + a.h:
                continue
            intersection = min(a.y + a.h, b.y + b.h) - max(a.y, b.y)
            union = a.h + b.h - intersection
            iou = np.clip(intersection / union if union > 0 else 0, 0, 1)
            dist_mat[i, j] = dist_mat[j, i] = 1 - iou

    dbscan = DBSCAN(
        eps=max_dist,
        min_samples=min_words_per_line,
        metric='precomputed').fit(dist_mat)

    clustered = defaultdict(list)
    for i, cluster_id in enumerate(dbscan.labels_):
        if cluster_id == -1:
            continue
        clustered[cluster_id].append(bboxes[i])

    lines = sorted(
        clustered.values(),
        key=lambda line: [bbox.y + bbox.h / 2 for bbox in line])

    return lines


def sort_multiline(
        bboxes: list[BBox],
        max_dist: float = 0.7,
        min_words_per_line: int = 1
        ) -> list[BBox]:
    """Cluster detections into lines, then sort the lines according to
    x-coordinates of word centers.

    ### Args:
        `bboxes`: List of bounding boxes.
        `max_dist`: Maximum Jaccard distance (0..1) between two y-projected
        words to be considered as neighbors.
        `min_words_per_line`: If a line contains less words than specified, it
        is ignored.

    ### Returns:
        List of bboxes sorted from top to bottom and left to right.
    """
    lines = _cluster_lines(bboxes, max_dist, min_words_per_line)
    result = []
    for line in lines:
        result.extend(sort_line(line))

    return result


def sort_line(
        bboxes: list[BBox]
        ) -> list[BBox]:
    """Sort the list of detections according to x-coordinates of word
    centers.

    ### Args:
        `bboxes`: List of bounding boxes.

    ### Returns:
        List of bboxes sorted from left to right.
    """
    return sorted(bboxes, key=lambda bbox: bbox.x + bbox.w / 2)


def main():
    pass


if __name__ == '__main__':
    main()
