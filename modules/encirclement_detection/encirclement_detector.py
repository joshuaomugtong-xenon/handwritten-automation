import cv2
import numpy as np


class EncirclementDetector:
    def detect(self, img_gray, min_area=0.15, max_area=0.9) -> bool:
        # Binarization
        _, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)

        # Contour Finding
        img_blur = cv2.GaussianBlur(img_binary, (3, 3), sigmaX=0, sigmaY=0)
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)
        contours, _ = cv2.findContours(
            edges, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

        # Contour Filtering
        orig_height, orig_width = img_gray.shape
        radius = min(orig_height, orig_width) / 3
        img_x, img_y = orig_width / 2, orig_height / 2
        contours_filtered = []
        for i, cnt in enumerate(contours):
            if hierarchy[0][i][3] != -1:
                continue
            cnt = cv2.convexHull(cnt)
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue
            cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            dist = np.sqrt((cX - img_x) ** 2 + (cY - img_y) ** 2)
            if dist > radius:
                continue
            if not self._check_shape(cnt):
                continue


            x, y, w, h = cv2.boundingRect(cnt)
            if w * h < 0.2 * orig_height * orig_width:
                continue

            contours_filtered.append(cnt)

        # Largest Contour and Area Check
        largest_cnt = max(contours_filtered, key=cv2.contourArea, default=None)

        if largest_cnt is not None:
            has_circle = self._check_area(
                largest_cnt, min_area, max_area, orig_height * orig_width)
        else:
            has_circle = False

        # Return True or False
        return has_circle

    def _check_area(self, cnt, min_area, max_area, orig_area):
        cnt_area = cv2.contourArea(cnt)
        area_ratio = cnt_area / orig_area
        return min_area <= area_ratio <= max_area
        
    def _check_shape(self, cnt):
        perimeter = cv2.arcLength(cnt, True)
        area = cv2.contourArea(cnt)
        if perimeter == 0:
            return False
        circularity = 4 * np.pi * (area / (perimeter ** 2))
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / h if h != 0 else 0
        if aspect_ratio < 1:
            aspect_ratio = 1 / aspect_ratio
        dynamic_threshold = max(0.6, 0.95 - (aspect_ratio - 1) * 0.2)
        return circularity > dynamic_threshold
