import torch
import torch.nn as nn

def get_device() -> torch.device:
    if torch.cuda.is_available(): return torch.device('cuda')
    elif torch.backends.mps.is_available(): return torch.device('mps')
    else: return torch.device('cpu')

def get_param_count(model: nn.Module) -> tuple[int, dict]:
    layer_params = {}
    for layer_name, param in model.named_parameters():
        layer_params[layer_name] = layer_params.get(layer_name, 0) + param.numel()
    total_params = sum(layer_params.values())
    return total_params, layer_params
        
def get_loader_stats(loader: torch.utils.data.DataLoader, channel_wise: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
    mean, std = 0, 0
    for data, _ in loader:
        if channel_wise:
            mean += data.mean(dim=(0, 2, 3))
            std += data.std(dim=(0, 2, 3))
        else:
            mean += data.mean()
            std += data.std()
    mean /= len(loader)
    std /= len(loader)
    return mean, std