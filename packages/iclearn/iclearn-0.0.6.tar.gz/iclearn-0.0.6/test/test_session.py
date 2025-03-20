import os
from pathlib import Path
import shutil

from iccore.test_utils import get_test_output_dir

from icflow import environment

from iclearn.model import Metrics
from iclearn.output import LoggingOutputHandler
from iclearn.session import Session

from mocks import MockDataloader, MockLossFunc, MockModel
from mocks.images import generate_images


def test_session():

    work_dir = get_test_output_dir()
    dataset = generate_images(work_dir, number=20, splits=[0.5, 0.25])

    # Load the runtime environment for the session
    env = environment.load()

    # Set up the dataloader
    batch_size = 5
    dataloader = MockDataloader(dataset, batch_size)

    # Collect anything 'model' related in a single object
    loss_func = MockLossFunc()
    metrics = Metrics(loss_func)
    model = MockModel(metrics)

    # This is a single machine learning 'experiment'
    result_dir = work_dir / "results"
    session = Session(
        model,
        env,
        result_dir,
        dataloader,
        output_handlers=[LoggingOutputHandler(result_dir)],
    )

    num_epochs = 1
    session.train(num_epochs)

    metrics.reset()
    session.infer()

    # Clean up after ourselves
    shutil.rmtree(work_dir)
