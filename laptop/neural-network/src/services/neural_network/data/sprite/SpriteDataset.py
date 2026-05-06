import os.path
from collections.abc import Callable

import numpy as np
import pandas as pd
import torch
from PIL import Image
from pandas import DataFrame
from torch.utils.data import Dataset
from skimage import io, transform


# https://docs.pytorch.org/tutorials/beginner/data_loading_tutorial.html
class SpriteDataset(Dataset):
    """Classification dataset for all of our sprites"""

    def __init__(self, csv_file: str, root_directory: str, transform: Callable = None):
        """
        Args:
            csv_file (str): Path to the csv file with annotations.
            root_directory (str): Directory with all the images.
            transform (callable): Optional transform to be applied on a sample. (optional)
        """
        self.labelled_sprites: DataFrame = pd.read_csv(csv_file)
        self.root_directory: str = root_directory
        self.transform: Callable | None = transform

    def __len__(self):
        return len(self.labelled_sprites)

    def __getitem__(self, index):
        if torch.is_tensor(index):
            index = index.tolist()

        image_name = os.path.join(self.root_directory, self.labelled_sprites.iloc[index, 0])
        image = io.imread(image_name)
        classification = self.labelled_sprites.iloc[index, 1:]
        classification = np.array(self.labelled_sprites.iloc[index, 1:], dtype=float)
        classification = torch.argmax(torch.from_numpy(classification), dim=0)
        sample = { "image": image, "classification": classification }

        if self.transform:
            sample["image"] = self.transform(sample["image"])

        return sample