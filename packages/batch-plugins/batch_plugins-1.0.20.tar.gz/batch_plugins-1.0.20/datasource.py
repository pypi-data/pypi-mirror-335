from abc import ABC, abstractmethod

class DataSource(ABC):
    """ Include the pipeline_conf argument and assignment
    @abstractmethod
    def __init__(self, pipeline_conf: dict, download_dir: str) -> None:
        self.pipeline_conf = pipeline_conf
        self.download_dir = download_dir
        self.file_extension = self.pipeline_conf['ingestion']['file']['namePattern'].replace('.', '')
        self.remote_path = self.pipeline_conf['ingestion']['source']['path']
        self.landing_zone_bucket = self.pipeline_conf['ingestion']['landingZone']
    """

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def read_data(self) -> None:
        pass

    @abstractmethod
    def transform_data(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass