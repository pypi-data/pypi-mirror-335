"""
Handle CLI arguments for the preview function
"""

from pathlib import Path
import logging
from typing import Callable

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Config(BaseModel, frozen=True):

    batch_size: int = 64
    dataset_dir: Path = Path()
    result_dir: Path = Path()


def cli_func(dataset_func: Callable, args):

    config = Config(dataset_dir=args.dataset_dir, result_dir=args.result_dir)

    logger.info("Previewing dataset at: %s", config.dataset_dir)
    _ = dataset_func(config.dataset_dir, config.batch_size)

    logger.info("Doing dataset preview")


def add_parser(parent):

    parser = parent.add_parser("preview", help="Run in preview mode")
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
