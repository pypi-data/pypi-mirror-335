"""
Module to support creating and launching a training session from the CLI
"""

import os
import logging
from pathlib import Path
from typing import Callable
from functools import partial

from pydantic import BaseModel
import torch

from iccore.serialization import write_model
from icflow.utils.profiler import TimerProfiler, ProfilerCollection

import iclearn.session
from iclearn.environment.torch import environment
from iclearn.utils.torch.profiler import TorchProfiler
from iclearn.output import LoggingOutputHandler, PlottingOutputHandler

logger = logging.getLogger(__name__)


class Config(BaseModel, frozen=True):

    num_epochs: int
    num_batches: int
    batch_size: int
    learning_rate: float
    node_id: int = 0
    num_nodes: int = 1
    num_gpus: int = 1
    local_rank: int = 0
    with_profiling: bool = False
    dataset_dir: Path = Path()
    result_dir: Path = Path()


def write_config(config: Config, path: Path):
    write_model(config, path / "config.json")


def setup_session(dataset_func: Callable, model_func: Callable, config: Config):

    logger.info("Starting session in: %s", config.result_dir)
    write_config(config, config.result_dir)

    logger.info("Setting up profilers")
    profilers = ProfilerCollection()
    profilers.add_profiler("timer", TimerProfiler(config.result_dir))
    if config.with_profiling:
        profilers.add_profiler("torch", TorchProfiler(config.result_dir))
    profilers.start()

    logger.info("Loading environment")
    env = environment.load(
        config.node_id, config.num_nodes, config.num_gpus, config.local_rank
    )
    environment.write(env, config.result_dir)

    logger.info("Loading dataset from: %s", config.dataset_dir)
    dataset = dataset_func(config.dataset_dir, config.batch_size)

    logger.info("Creating Model")
    model = model_func(dataset.num_classes, config.learning_rate, config.num_batches)

    logger.info("Creating Session")
    session = iclearn.session.Session(model, env, config.result_dir, dataset)
    session.output_handlers.extend(
        [
            LoggingOutputHandler(config.result_dir),
            PlottingOutputHandler(config.result_dir),
        ]
    )
    return profilers, session


def config_from_cli(args, local_rank: int):
    return Config(
        num_epochs=args.num_epochs,
        num_batches=args.num_batches,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        node_id=args.node_id,
        num_nodes=args.num_nodes,
        num_gpus=args.num_gpus,
        local_rank=local_rank,
        dataset_dir=args.dataset_dir.resolve(),
        result_dir=args.result_dir.resolve(),
    )


def worker(session_func: Callable, local_rank: int, args):
    """
    This is the entry point on each parallel worker
    """

    logger.info(
        "Starting worker with rank %s and result dir %s",
        local_rank,
        args.result_dir,
    )

    config = config_from_cli(args, local_rank)
    profilers, session = session_func(config)
    if args.dry_run == 1:
        return

    logger.info("Starting training stage")
    session.train(config.num_epochs)
    logger.info("Finished training stage")

    if session.runtime_ctx.is_master_process():
        logger.info("Doing inference on test set")
        session.infer()

    profilers.stop()
    logger.info(
        "Finised worker task. Runtime = %.2f minutes",
        profilers.profilers["timer"].get_runtime() / 60,
    )


def cli_func(session_func: Callable, args):

    if args.num_gpus > 1:
        os.environ["MASTER_ADDR"] = "localhost"  # Address for master node
        os.environ["MASTER_PORT"] = "9956"  # Port for comms with master node

        torch.multiprocessing.spawn(
            partial(worker, session_func), nprocs=args.num_gpus, args=(args,)
        )
    else:
        # Single GPU or CPU execution
        worker(session_func, 0, args)


def add_parser(parent):

    parser = parent.add_parser("train", help="Run in training mode")
    parser.add_argument(
        "--num-nodes", type=int, default=1, help="Number of nodes to run on"
    )
    parser.add_argument("--node-id", type=int, default=0, help="ID of the current node")
    parser.add_argument(
        "--num-gpus", type=int, default=1, help="Number of GPUs per node"
    )
    parser.add_argument(
        "--with_profiling", type=int, default=0, help="Enable profiling"
    )
    parser.add_argument("--with_mlflow", type=int, default=0, help="Enable MlFlow")
    parser.add_argument(
        "--num_workers", type=int, default=4, help="Number of dataloader workers"
    )
    parser.add_argument(
        "--num_epochs", type=int, default=15, help="Number of epochs for training"
    )
    parser.add_argument(
        "--num_batches", type=int, default=0, help="Max number of batches for training"
    )
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument(
        "--learning-rate", type=float, default=3e-4, help="Learning Rate"
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        default=Path(),
        help="Path to the directory containing datasets",
    )
    parser.add_argument(
        "--result_dir",
        type=Path,
        default=Path() / "results",
        help="Path to results directory",
    )
    return parser
