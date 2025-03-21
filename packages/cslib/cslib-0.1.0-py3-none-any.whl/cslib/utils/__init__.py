from .image import *
from .config import *
from .gui import *

import torch

def get_device(device: str = 'auto') -> torch.device:
    if device != 'auto':
        return torch.device(device)
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif torch.backends.mps.is_available():
        return torch.device('mps')
    else:
        return torch.device('cpu')