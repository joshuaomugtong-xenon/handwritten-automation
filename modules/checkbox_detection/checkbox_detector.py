import cv2


class CheckboxDetector:
    def __init__(self, lr_indent=0.20, tb_indent=0.20, pixel_threshold=0.85):
        self.lr_indent = lr_indent
        self.tb_indent = tb_indent
        self.pixel_threshold = pixel_threshold

    def detect(self, img_gray) -> bool:
        contours_list = self.find_all_contours(img_gray)
        largest_contour = self.get_largest_contour(contours_list)
        img_binary = self.binarize_image(img_gray)

        cropped_img = self.crop_contour(img_binary, largest_contour)
        return self.contains_black_pixels(cropped_img)

    def contains_black_pixels(self, img_binary):
        area = img_binary.shape[0] * img_binary.shape[1]
        pixel_percentage = cv2.countNonZero(img_binary) / area
        return pixel_percentage < self.pixel_threshold

    def binarize_image(self, img_gray):
        _, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)
        return img_binary

    def find_all_contours(self, img_gray):
        img_binary = self.binarize_image(img_gray)
        img_blur = cv2.GaussianBlur(img_binary, (3, 3), sigmaX=0, sigmaY=0)
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)
        contours, _ = cv2.findContours(
            edges, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def get_largest_contour(self, contours):
        largest_area = 0
        largest_contour = None

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            current_area = w * h
            if current_area > largest_area:
                largest_area = current_area
                largest_contour = contour
        return largest_contour

    def crop_contour(self, img_binary, contour):
        x, y, w, h = cv2.boundingRect(contour)

        tl_y = int(y + h * self.lr_indent)
        br_y = int(y + h * (1 - self.lr_indent))
        tl_x = int(x + w * self.tb_indent)
        br_x = int(x + w * (1 - self.tb_indent))

        return img_binary[tl_y:br_y, tl_x:br_x]
