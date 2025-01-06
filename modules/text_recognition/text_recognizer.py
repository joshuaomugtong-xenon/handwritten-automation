import os

import cv2
import numpy as np

try:
    from word_detector.word_detection import WordDetector
    from parseq.word_recognition import WordRecognizer
except ImportError:
    from .word_detector.word_detection import WordDetector
    from .parseq.word_recognition import WordRecognizer


class TextRecognizer:
    def __init__(self):
        self.word_detector = WordDetector()
        self.word_recognizer = WordRecognizer()

    def recognize_text(self, image: np.ndarray) -> str:
        # Extract the word images
        bboxes = self.word_detector.extract_words(image)

        word_images = []
        for bbox in bboxes:
            word_image = bbox.crop(image)
            word_images.append(word_image)

        # Extract the text from the word images
        text_list = []
        for word_image in word_images:
            word, c = self.word_recognizer.extract_text(word_image)
            # if confidence > 0.5:
            #     text_list.append(word)
            text_list.append(word)

        return ' '.join(text_list)


def main():
    root = os.getcwd()
    input_folder = 'misc'
    # input_folder = 'multiline word segment'
    # input_folder = 'text recognition test images'
    input_directory = os.path.join(root, input_folder)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    multiple = True
    detector = WordDetector()
    # recognizer = WordRecognizer()

    if multiple:
        dir: list[str] = os.listdir(input_directory)
        for filename in dir:
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                # Input path
                input_path = os.path.join(input_directory, filename)
                # Process image
                image = cv2.imread(input_path)
                bboxes = detector.extract_words(image) # noqa
                # word_images = []
                # for bbox in bboxes:
                #     word_image = bbox.crop(image)
                #     word_images.append(word_image)
                # # Extract the text from the word images
                # text_list = []
                # for word_image in word_images:
                #     word, c = recognizer.extract_text(word_image)
                #     # if confidence > 0.5:
                #     #     text_list.append(word)
                #     text_list.append(word)
                #     print(f'Confidence {c[0]:.5f}, mean: {np.mean(c):.5f} Word: \'{word}\'') # noqa
    else:
        # Input path
        input_path = os.path.join(input_directory, 'test07.png')

        # Process image
        image = cv2.imread(input_path)

        detector.extract_words(image)


if __name__ == '__main__':
    main()
