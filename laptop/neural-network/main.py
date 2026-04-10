import time

import numpy as np
import pandas as pd
import torch
from torch import nn

from data.InputOutputEnums import Thing, Track
from models.TrolleyProblemModel import TrolleyProblemModel
from models.utils.TrainingUtils import calculate_accuracy

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    model: TrolleyProblemModel = TrolleyProblemModel(n_input_features=4,
                                                     epochs=40,
                                                     loss_fn=nn.BCEWithLogitsLoss(),
                                                     eval_fn=calculate_accuracy,
                                                     learning_rate=0.1,
                                                     optimizer_class=torch.optim.SGD)

    testing_data = np.array([[Thing.HUMAN.value, 0.1, Thing.HUMAN.value, 50],
                             [Thing.HUMAN.value, 1, Thing.HUMAN.value, 99],
                             [Thing.HUMAN.value, 32, Thing.HUMAN.value, 5.4],
                             [Thing.HUMAN.value, 3.55, Thing.ALLIGATOR.value, 32],
                             [Thing.PIG.value, 1, Thing.HUMAN.value, 1],
                             [Thing.HUMAN.value, 1, Thing.HUMAN.value, 1.1],
                             [Thing.HUMAN.value, 56, Thing.HUMAN.value, 55],])
    testing_data = torch.from_numpy(testing_data).type(torch.float)
    print(f'untrained model inference: {model.inference(testing_data)}')

    training_data = pd.DataFrame({
        "Track_1_Thing": [
            Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN,
            Thing.NOTHING, Thing.ALLIGATOR, Thing.COW, Thing.FROG, Thing.KOALA, Thing.PIG,
            Thing.NOTHING, Thing.ALLIGATOR, Thing.COW, Thing.FROG, Thing.KOALA, Thing.PIG,
            Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN,
            Thing.NOTHING, Thing.COW, Thing.PIG, Thing.ALLIGATOR,
        ],
        "Track_1_Age": [
            5, 8, 13, 18, 25, 40,
            0, 0, 0, 0, 0, 0,
            30, 30, 30, 30, 30, 30,
            4, 15, 17, 65,
            4, 10, 2, 50,
        ],
        "Track_2_Thing": [
            Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN,
            Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN,
            Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN, Thing.HUMAN,
            Thing.NOTHING, Thing.ALLIGATOR, Thing.COW, Thing.PIG,
            Thing.COW, Thing.PIG, Thing.ALLIGATOR, Thing.FROG,
        ],
        "Track_2_Age": [
            13, 5, 40, 8, 80, 25,
            13, 13, 13, 13, 13, 13,
            13, 13, 13, 13, 13, 13,
            30, 30, 30, 30,
            12, 1, 9, 2,
        ],
        "Label": [
            Track.TWO, Track.ONE, Track.TWO, Track.ONE, Track.TWO, Track.ONE,
            Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE,
            Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE, Track.ONE,
            Track.TWO, Track.TWO, Track.TWO, Track.TWO,
            Track.TWO, Track.ONE, Track.TWO, Track.ONE,
        ]
    })

    X = training_data[["Track_1_Thing", "Track_1_Age", "Track_2_Thing", "Track_2_Age"]].copy()
    y = training_data["Label"].copy()

    # Convert Enum -> int
    X["Track_1_Thing"] = X["Track_1_Thing"].map(lambda t: t.value)
    X["Track_2_Thing"] = X["Track_2_Thing"].map(lambda t: t.value)
    y = y.map(lambda t: t.value)

    # convert to numpy otherwise pytorch is unhappy when we convert to tensors
    X = X.to_numpy(copy=True)
    y = y.to_numpy(copy=True)

    # Turn data into tensors
    # Otherwise this causes issues with computations later on
    X = torch.from_numpy(X).type(torch.float)
    y = torch.from_numpy(y).type(torch.float)

    start_time = time.perf_counter()
    model.train(X, y)

    # https://discuss.pytorch.org/t/access-all-weights-of-a-model/77672/12
    #print(model.model.parameters())

    print(f'trained model inference: {model.inference(testing_data)}')
    end_time = time.perf_counter()
    print(f'elapsed time for train and inference was {end_time - start_time:.3f}s')



