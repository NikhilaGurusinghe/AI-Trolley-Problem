# adapted from https://docs.pytorch.org/tutorials/beginner/data_loading_tutorial.html#transforms
import numpy as np
import torch
from skimage import transform

class Rescale(object):
    """Rescale the image in a sample to a given size.

    Args:
        output_size (tuple or int): Desired output size. If tuple, output is
            matched to output_size. If int, smaller of image edges is matched
            to output_size keeping aspect ratio the same.
    """

    def __init__(self, output_size: tuple | int):
        assert isinstance(output_size, (int, tuple))
        self.output_size: tuple | int = output_size

    def __call__(self, sample):
        image, classification = sample["image"], sample["classification"]

        height, width = image.shape[:2]
        if isinstance(self.output_size, int):
            if height > width:
                new_height, new_width = self.output_size * height / width, self.output_size
            else:
                new_height, new_width = self.output_size, self.output_size * width / height
        else:
            new_height, new_width = self.output_size

        new_height, new_width = int(new_height), int(new_width)

        resized_image = transform.resize(image, (new_height, new_width))

        return {"image": resized_image, "classification": classification}

class RandomCrop(object):
    """Crop randomly the image in a sample.

    Args:
        output_size (tuple or int): Desired output size. If int, square crop
            is made.
    """

    def __init__(self, output_size: tuple | int):
        assert isinstance(output_size, (int, tuple))
        if isinstance(output_size, int):
            self.output_size: tuple = (output_size, output_size)
        else:
            assert len(output_size) == 2 # i.e. output_size is a tuple
            self.output_size: tuple = output_size

    def __call__(self, sample):
        image, classification = sample["image"], sample["classification"]

        height, width = image.shape[:2]
        new_height, new_width = self.output_size

        top = torch.randint(0, height - new_height + 1, (1,))
        left = torch.randint(0, width - new_width + 1, (1,))

        image = image[top: top + new_height, left: left + new_width]

        return {"image": image, "classification": classification}

class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample):
        image, classification = sample["image"], sample["classification"]

        # swap color axis because
        # numpy image: H x W x C
        # torch image: C x H x W
        image = image.transpose((2, 0, 1))
        return {"image": torch.from_numpy(image), "classification": torch.from_numpy(classification)}