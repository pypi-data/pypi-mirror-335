import random
import numpy as np

import warnings

reqs = ['torch']

try:
    import torch


    def torch_seed(seed=0):
        """
        设置 PyTorch 的随机种子以确保结果可复现。

        :param seed: 要使用的随机种子，默认为 0。
        """
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

except ImportError:
    warnings.warn(
        "PyTorch 未安装。请使用以下命令安装 PyTorch：\n"
        "pip install torch\n"
        "或访问 PyTorch 官网获取更多安装信息：https://pytorch.org/",
        UserWarning
    )


def normal_seed(seed=0):
    random.seed(seed)
    np.random.seed(seed)
