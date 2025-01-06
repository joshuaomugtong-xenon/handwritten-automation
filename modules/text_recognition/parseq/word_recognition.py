import numpy as np
import cv2
import torch
import torchvision.transforms as T
from PIL import Image


class WordRecognizer:
    def __init__(self):
        self.model = torch.hub.load('baudm/parseq', 'parseq', pretrained=True)
        self.model.eval()
        self.transform = T.Compose([
            T.Resize(self.model.hparams.img_size, T.InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(0.5, 0.5),
        ])

    def extract_text(self, image: np.ndarray) -> tuple[str, np.ndarray]:
        # Input is a numpy array loaded using cv2

        # Convert to PIL image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        # Preprocess the image and convert to tensor
        image_tensor: torch.Tensor = self.transform(image)

        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)

        # Get the logits
        with torch.no_grad():
            logits: torch.Tensor = self.model(image_tensor)
            # Get the prediction
            prediction = logits.softmax(-1)

        # Decode the prediction
        label, confidence = self.model.tokenizer.decode(prediction)

        word, confidence = label[0], confidence[0]

        return word, confidence.numpy()


def main():
    pass


if __name__ == '__main__':
    main()
