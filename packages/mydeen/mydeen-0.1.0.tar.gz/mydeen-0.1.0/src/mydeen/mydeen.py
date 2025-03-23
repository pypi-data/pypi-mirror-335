from .metasurahs import MetaSurahs
from .meta_quran_reader import MetaQuranReader
from .yt_services import YoutubeServices
from .config import Config
from pathlib import Path


class MyDeen:
    def __init__(self):
        path = Path(__file__).parent / 'data'
        path.mkdir(parents=True, exist_ok=True)
        self.path_database = path.as_posix()
        self.setup_all()

    def config_url(self) -> Config:
        return Config()

    def meta_surahs(self) -> MetaSurahs:
        return MetaSurahs(self.path_database)


    def quran_reader(self) -> MetaQuranReader:
        return MetaQuranReader(self.path_database)
    
    def yt_services(self, api_key: str) -> YoutubeServices:
        return YoutubeServices(api_key)

    def setup_all(self) -> None:
        self.meta_surahs()
        self.quran_reader()
