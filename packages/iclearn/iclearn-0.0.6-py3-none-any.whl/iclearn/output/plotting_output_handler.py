"""
This module allows for plotting results during a session
"""

from pathlib import Path
import logging

# from icplot.graph import DatasetGridPlot, MultiFigureLinePlot

from iclearn.data import Dataloader

from .output_handler import OutputHandler

logger = logging.getLogger(__name__)


class PlottingOutputHandler(OutputHandler):
    def __init__(self, result_dir: Path = Path(), num_images: int = 20):
        super().__init__(result_dir)

        self.num_images = num_images
        self.pre_epoch_image_path = "train_sample"
        self.figure_infos = [
            {
                "key": "iou",
                "label": "IoU",
                "title": "Mean Initersection Over Union",
            },
            {
                "key": "pa",
                "label": "Pixel Accuracy",
                "title": "Pixel Accuracy",
            },
            {
                "key": "loss",
                "label": "Loss",
                "title": "Loss Value",
            },
        ]

        # self.dataset_plotter = DatasetGridPlot()

    def on_before_epochs(self, num_epochs: int, dataloader: Dataloader):
        logger.info("Plotting dataset sample")
        # output_path = self.result_dir / self.pre_epoch_image_path
        # self.dataset_plotter.plot(
        #     dataset.get_data("train"),
        #     self.num_images,
        #     output_path,
        #     dataset.transform,
        # )

    def on_after_infer(self, stage, predictions, metrics):
        super().on_after_infer(stage, predictions, metrics)

        # for figure_info in self.figure_infos:
        # line_plot = MultiFigureLinePlot(metrics, figure_info, "Step")
        # line_plot.plot(self.result_dir / "post_infer_metrics")
