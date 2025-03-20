import os
from pathlib import Path
import shutil

from iccore.test_utils import get_test_output_dir

from icflow import environment

from iclearn.data.split import get_fractional_splits
from iclearn.model import Metrics
from iclearn.output import LoggingOutputHandler
from iclearn.session import Session

from mocks.linear import LinearDataloader, LinearLossFunc, LinearModel


def test_regression():

    work_dir = get_test_output_dir()

    # Load the runtime environment for the session
    env = environment.load()

    # Set up the dataloader
    splits = get_fractional_splits(0.75, 0.25)
    dataloader = LinearDataloader(
        w=0.5, b=0.5, num_points=20, batch_size=5, splits=splits, env=env
    )

    # Collect anything 'model' related in a single object
    loss_func = LinearLossFunc()
    model = LinearModel(metrics=Metrics(loss_func))

    # This is a single machine learning 'experiment'
    result_dir = work_dir / "results"
    session = Session(
        model,
        env=env,
        dataloader=dataloader,
        output_handlers=[LoggingOutputHandler(result_dir)],
    )

    num_epochs = 1
    session.train(num_epochs)


#    metrics.reset()
#    session.infer()

# Clean up after ourselves
#    shutil.rmtree(work_dir)
