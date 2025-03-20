import logging
import platform
from pathlib import Path

import torch

from iccore.serialization import write_model
from icsystemutils.network import info
from icsystemutils.cpu import process, cpu_info

from icflow.environment import Environment

from .dist_utils import sync_dict, load_torch_info, TorchInfo
from .cuda_info import load_cuda_info, CudaInfo

logger = logging.getLogger(__name__)


class TorchDevice:
    """
    This represents a compute device, such as a GPU or CPU
    """

    def __init__(self):
        if torch.cuda.is_available():
            self.name = f"cuda:{self.local_rank}"
        else:
            self.name = "cpu"
        logger.info("Loading torch device %s", self.name)
        self.handle = torch.device(self.name)


class TorchEnvironment(Environment):
    """
    This holds runtime information for the session, which is mostly
    useful in a distributed setting.
    """

    torch_info: TorchInfo
    cuda_info: CudaInfo
    dist_backend: str = "nccl"

    def sync_dict(self, input_dict: dict, device) -> dict:
        """
        If we are running in on multiple gpus sync dict across devices
        """

        if not self.is_multigpu:
            return input_dict
        return sync_dict(input_dict, device)


def load(
    node_id: int = 0, num_nodes: int = 1, num_gpus: int = 1, local_rank: int = 0
) -> TorchEnvironment:
    """
    Read system information for logging and consumption in
    a machine learning session.
    """

    return TorchEnvironment(
        torch_info=load_torch_info(),
        cuda_info=load_cuda_info(),
        node_id=node_id,
        num_nodes=num_nodes,
        gpus_per_node=num_gpus,
        process=process.load(local_rank),
        network=info.load(),
        cpu_info=cpu_info.read(),
        platform=platform.platform(),
    )


def write(
    env: TorchEnvironment, path: Path, filename: str = "environment.json"
) -> None:
    write_model(env, path / filename)
