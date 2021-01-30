from abc import ABC, abstractmethod
from app.utils.web_utils import managed_session


class BaseParser(ABC):
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
