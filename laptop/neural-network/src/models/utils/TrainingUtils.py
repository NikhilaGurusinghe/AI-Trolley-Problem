import torch

from sklearn.model_selection import train_test_split

def get_train_test_split(X: torch.Tensor,
                         y: torch.Tensor,
                         random_seed: int,
                         test_size: float = 0.2) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    return train_test_split(X, y, test_size=test_size, random_state=random_seed)

def calculate_accuracy(y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
    assert len(y_true) == len(y_pred)
    # print("y_true", y_true.shape)
    # print("y_true", y_true)
    # print("y_pred", y_pred.shape)
    # print("y_pred", y_pred)

    correct = torch.eq(y_true, y_pred).sum().item()
    accuracy = (correct / len(y_true)) * 100
    return accuracy