"""
This module has functionaly for loading data from
an iclearn dataset - which is essentially a path to some data.

It differs from a PyTorch dataloader in that it manages 'splits' (test, train, val)
etc - it holds PyTorch-like dataloaders for each split.
"""

from pathlib import Path
import logging

from icflow.environment import Environment
from icflow.data import Dataset

from .split import Splits, get_default_splits

logger = logging.getLogger(__name__)


class Dataloader:
    """
    This class supports loading data from a provided dataset

    :param Dataset dataset: The dataset (data location) to load from
    :param int batch_size: The size of batches to load at runtime
    :param Splits splits: Description of how to split the dataset
    :param Environment env: The runtime context or environment
    """

    def __init__(
        self,
        dataset: Dataset,
        batch_size: int,
        splits: Splits | None = None,
        env: Environment | None = None,
    ):
        self.datasets: dict = {}
        self.loaders: dict = {}
        self.samplers: dict = {}

        self._load(dataset, splits, batch_size, env)

    def _load(
        self,
        dataset: Dataset,
        splits: Splits | None,
        batch_size: int,
        env: Environment | None,
    ) -> None:
        """
        Load the dataset from the supplied path
        """
        logger.info("Loading dataset from %s", dataset.path)

        if not dataset.is_readable:
            raise RuntimeError("Provided dataset is not readable")

        if not splits:
            logger.info("No splits specifed - loading defaults")
            splits = get_default_splits()

        for s in splits.items:
            self._load_dataset(dataset.path, s.name, splits)
        self._setup_dataloaders(splits, batch_size, env)

        logger.info(
            "Finished loading dataset with %d dataloaders", len(self.datasets.keys())
        )

    def _load_dataset(self, root: Path, name: str, splits: Splits):
        self.datasets[name] = self.load_dataset(root, name, splits)

    def load_dataset(self, root: Path, name: str, splits: Splits):
        """
        Override this to provide a PyTorch-like dataset
        """
        raise NotImplementedError()

    def load_sampler(self, data, num_replicas, rank):
        """
        Override to provide a distributed sampler
        """
        return None

    def load_dataloader(self, dataset, batch_size, shuffle, sampler, num_workers):
        """
        Override to provide a PyTorch-like dataloader
        """
        raise NotImplementedError()

    def get_dataset(self, name: str):
        """
        Get the dataset for named split
        """
        return self.datasets[name]

    def get_dataloader(self, name: str):
        """
        Get the dataloader for a named split
        """
        return self.loaders[name]

    def num_batches(self, name: str) -> int:
        return len(self.loaders[name])

    @property
    def num_classes(self) -> int:
        if self.datasets:
            dataset = list(self.datasets.values())[0]
            if hasattr(dataset, "num_classes"):
                return getattr(dataset, "num_classes")
        return 0

    def on_epoch_start(self, epoch_idx: int):
        self._set_sampler_epoch(epoch_idx)

    def _set_sampler_epoch(self, epoch: int):
        for sampler in self.samplers.values():
            sampler.set_epoch(epoch)

    def _setup_dataloaders(
        self,
        splits: Splits,
        batch_size: int,
        env: Environment | None = None,
    ) -> None:
        """
        Set up a dataloader for each split and if supported a
        data sampler
        """
        if env and env.is_multigpu:
            logger.info("Setting up Samplers")
            for split in [s for s in splits.items if s.use_sampler]:
                sampler = self.load_sampler(
                    self.datasets[split.name],
                    env.world_size,
                    env.global_rank,
                )
                if sampler:
                    self.samplers[split.name] = sampler

        logger.info("Setting up Dataloaders")
        for (name, dataset), attrs in zip(self.datasets.items(), splits.items):
            self.loaders[name] = self.load_dataloader(
                dataset,
                batch_size,
                attrs.shuffle,
                sampler=self.samplers[name] if name in self.samplers else None,
                num_workers=env.cpu_info.cores_per_node if env else 1,
            )
