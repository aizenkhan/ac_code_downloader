from abc import ABC, abstractmethod
from app.utils.web_utils import managed_session


class BaseParser(ABC):
    def __init__(self, __dict_urls={}) -> None:
        self.__dict_urls = __dict_urls

    def add_url(self, url_name, url):
        self.__dict_urls[url_name] = url

    def remove_url(self, url_key):
        del self.__dict_urls[url_key]

    def get_url(self, url_key):
        return self.__dict_urls.get(url_key)

    @abstractmethod
    def preprocess(self, session, *args, **kwargs):
        pass

    @abstractmethod
    def process(self, session, *args, **kwargs):
        pass

    def run(self):
        with managed_session() as session:
            self.preprocess(session)
            self.process(session)
