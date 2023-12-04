from typing import Union

import torch


def one_hot(
    tensor: torch.Tensor,
    num_classes: int,
    ignored_label: Union[str, int] = "negative",
):
    """An advanced version of F.one_hot with ignore label support. Convert the mask to a one-hot encoded representation by @visualDust

    Args:
        tensor (torch.Tensor): indexed label image. Should types int
        num_classes (int): number of classes
        ignored_label (Union[str|int], optional): specify labels to ignore, or ignore by pattern. Defaults to "negative".

    Returns:
        torch.Tensor: one hot encoded tensor
    """
    original_shape = tensor.shape
    for _ in range(4 - len(tensor.shape)):
        tensor = tensor.unsqueeze(0)  # H W -> C H W -> B C H W, if applicable
    # start to handle ignored label
    # convert ignored label into positive index bigger than num_classes
    if type(ignored_label) is int:
        tensor[tensor == ignored_label] = num_classes
    elif ignored_label == "negative":
        tensor[tensor < 0] = num_classes

    # check if mask image is valid
    if torch.max(tensor) > num_classes:
        raise RuntimeError("class values must be smaller than num_classes.")
    B, _, H, W = tensor.shape
    one_hot = torch.zeros(B, num_classes + 1, H, W)
    one_hot.scatter_(1, tensor, 1)  # mark 1 on channel(dim=1) with index of mask
    one_hot = one_hot[:, :num_classes]  # remove ignored label(s)
    for _ in range(len(one_hot.shape) - len(original_shape)):
        one_hot.squeeze_(0)  # B C H W -> H W ->  C H W, if applicable
    return one_hot
