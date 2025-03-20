from pathlib import Path
import logging

from pydantic import BaseModel

from icsystemutils.network import remote

logger = logging.getLogger(__name__)


class ModelMetadata(BaseModel, frozen=True):
    """
    A basic 'model' abstraction. Models can be referenced via a name and
    location, which can be remote.
    """

    name: str
    location: Path
    hostname: str = ""
    archive_name: str = ""

    @property
    def archive_path(self):
        return self.location / Path(self.name) / Path(self.archive_name)


def upload(model: ModelMetadata, host: remote.Host, local_location: Path):
    remote.upload(local_location, host, model.archive_path, None)


def download(model: ModelMetadata, host: remote.Host, local_location: Path):
    remote.download(host, model.archive_path, local_location, None)
