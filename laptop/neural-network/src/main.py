import asyncio
import os
import time

import numpy as np
import pandas as pd
import torch
import torchmetrics
from torch import nn
import matplotlib.pyplot as plt
from skimage import io, transform
from torch.utils.data import DataLoader, sampler, RandomSampler
from torchvision import transforms, utils
from torchvision.transforms import InterpolationMode

from data.InputOutputEnums import Entity, Track
from data.Transforms import *
from data.sprite.SpriteDataset import SpriteDataset
from models.SpriteRecognitionModel import SpriteRecognitionModel
from models.TrolleyProblemModel import TrolleyProblemModel
from models.utils.TrainingUtils import calculate_accuracy
from websocket.server import Server

# TTS library https://github.com/nateshmbhat/pyttsx3

activation = {}
def get_activation(name):
    def hook(model, input, output):
        activation[name] = output.detach()
    return hook

if __name__ == '__main__':
    # model: TrolleyProblemModel = TrolleyProblemModel(n_input_features=4,
    #                                                  epochs=40,
    #                                                  loss_fn=nn.BCEWithLogitsLoss(),
    #                                                  eval_fn=calculate_accuracy,
    #                                                  learning_rate=0.1,
    #                                                  optimizer_class=torch.optim.SGD)
    #
    # testing_data = np.array([[Entity.HUMAN.value, 0.1, Entity.HUMAN.value, 50],
    #                          [Entity.HUMAN.value, 1, Entity.HUMAN.value, 99],
    #                          [Entity.HUMAN.value, 32, Entity.HUMAN.value, 5.4],
    #                          [Entity.HUMAN.value, 3.55, Entity.ALLIGATOR.value, 32],
    #                          [Entity.PIG.value, 1, Entity.HUMAN.value, 1],
    #                          [Entity.HUMAN.value, 1, Entity.HUMAN.value, 1.1],
    #                          [Entity.HUMAN.value, 56, Entity.HUMAN.value, 55], ])
    # testing_data = torch.from_numpy(testing_data).type(torch.float)
    # print(f'untrained model inference: {model.inference(testing_data)}')
    #
    # training_data = pd.DataFrame({
    #     "Track_1_Thing": [
    #         Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN,
    #         Entity.NOTHING, Entity.ALLIGATOR, Entity.COW, Entity.FROG, Entity.KOALA, Entity.PIG,
    #         Entity.NOTHING, Entity.ALLIGATOR, Entity.COW, Entity.FROG, Entity.KOALA, Entity.PIG,
    #         Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN,
    #         Entity.NOTHING, Entity.COW, Entity.PIG, Entity.ALLIGATOR,
    #     ],
    #     "Track_1_Age": [
    #         5, 8, 13, 18, 25, 40,
    #         0, 0, 0, 0, 0, 0,
    #         30, 30, 30, 30, 30, 30,
    #         4, 15, 17, 65,
    #         4, 10, 2, 50,
    #     ],
    #     "Track_2_Thing": [
    #         Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN,
    #         Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN,
    #         Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN, Entity.HUMAN,
    #         Entity.NOTHING, Entity.ALLIGATOR, Entity.COW, Entity.PIG,
    #         Entity.COW, Entity.PIG, Entity.ALLIGATOR, Entity.FROG,
    #     ],
    #     "Track_2_Age": [
    #         13, 5, 40, 8, 80, 25,
    #         13, 13, 13, 13, 13, 13,
    #         13, 13, 13, 13, 13, 13,
    #         30, 30, 30, 30,
    #         12, 1, 9, 2,
    #     ],
    #     "Label": [
    #         Track.TWO, Track.ONE, Track.TWO, Track.ONE, Track.TWO, Track.ONE,
    #         Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE,
    #         Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE,
    #         Track.TWO, Track.TWO, Track.TWO, Track.TWO,
    #         Track.TWO, Track.ONE, Track.TWO, Track.ONE,
    #     ]
    # })
    #
    # X = training_data[["Track_1_Thing", "Track_1_Age", "Track_2_Thing", "Track_2_Age"]].copy()
    # y = training_data["Label"].copy()
    #
    # # Convert Enum -> int
    # X["Track_1_Thing"] = X["Track_1_Thing"].map(lambda t: t.value)
    # X["Track_2_Thing"] = X["Track_2_Thing"].map(lambda t: t.value)
    # y = y.map(lambda t: t.value)
    #
    # # convert to numpy otherwise pytorch is unhappy when we convert to tensors
    # X = X.to_numpy(copy=True)
    # y = y.to_numpy(copy=True)
    #
    # # Turn data into tensors
    # # Otherwise this causes issues with computations later on
    # X = torch.from_numpy(X).type(torch.float)
    # y = torch.from_numpy(y).type(torch.float)
    #
    # start_time = time.perf_counter()
    # model.train(X, y)
    #
    # # https://discuss.pytorch.org/t/access-all-weights-of-a-model/77672/12
    # #print(model.model.parameters())
    #
    # print(f'trained model inference: {model.inference(testing_data)}')
    # end_time = time.perf_counter()
    # print(f'elapsed time for train and inference was {end_time - start_time:.3f}s')
    #
    # # https://discuss.pytorch.org/t/access-all-weights-of-a-model/77672
    # for name, param in model.model.named_parameters():
    #     print(name, param, param.size())

    # image_height: int = 18
    # image_width: int = 10
    # sprite_dataset = SpriteDataset("../datasets/sprite/labelled_sprites.csv",
    #                                "../datasets/sprite/",
    #                                transforms.Compose([
    #                                    transforms.ToPILImage(),
    #                                    transforms.Pad(5, (255, 255, 255)),
    #                                    transforms.RandomCrop((image_height, image_width)),
    #                                    transforms.RandomHorizontalFlip(),
    #                                    transforms.Grayscale(1),
    #                                    # transforms.RandomRotation(6, InterpolationMode.NEAREST_EXACT, fill=(255, 255, 255)),
    #                                    # transforms.RandomPerspective(0.15, 0.9),
    #                                    transforms.ToTensor()
    #                                ]))
    #
    # sampler = RandomSampler(sprite_dataset, replacement=True, num_samples=100)
    # sprite_dataset_dataloader = DataLoader(sprite_dataset, batch_size=5, num_workers=0, sampler=sampler)

    # for i_batch, sample_batched in enumerate(sprite_dataset_dataloader):
    #     print(i_batch, sample_batched["image"].size(), sample_batched["classification"].size())
    #
    #     if i_batch == 12:
    #         plt.figure()
    #         images_batch, classification_batch = sample_batched["image"], sample_batched["classification"]
    #         batch_size = len(images_batch)
    #         image_size = images_batch.size()
    #
    #         grid = utils.make_grid(images_batch)
    #         plt.imshow(grid.numpy().transpose((1, 2, 0)))
    #         plt.ioff()
    #         plt.show()
    #         break

    # start_time = time.perf_counter()
    # sprite_recognition_model: SpriteRecognitionModel = SpriteRecognitionModel(image_width=image_width,
    #                                                   image_length=image_height,
    #                                                   n_colour_channels=1,
    #                                                   hidden_units=10,
    #                                                   output_shape=2,
    #                                                   epochs=50,
    #                                                   loss_fn=nn.CrossEntropyLoss(),
    #                                                   eval_fn=calculate_accuracy,
    #                                                   learning_rate=0.1,
    #                                                   optimizer_class=torch.optim.SGD)
    #
    # sprite_recognition_model.train(sprite_dataset_dataloader)

    # # https://discuss.pytorch.org/t/visualize-feature-map/29597/2
    # sprite_recognition_model.model.block_1.register_forward_hook(get_activation('block_1'))
    # data = next(iter(sprite_dataset_dataloader))["image"]
    # print(data.shape)
    # # data = torch.squeeze(data)
    # # print(data.shape)
    # output = sprite_recognition_model.inference(data)
    #
    # act = activation["block_1"]
    # fig, axarr = plt.subplots(act.size(0))
    # for idx in range(act.size(0)):
    #     axarr[idx].imshow(act[idx])
    #
    # plt.show()


    # end_time = time.perf_counter()
    # print(f'elapsed time for train and inference was {end_time - start_time:.3f}s')
    # print("started:")

    server: Server = Server("", port_number=8001)
    print("Server started!")
    asyncio.run(server.loop())
