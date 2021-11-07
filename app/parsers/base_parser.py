from abc import ABC, abstractmethod
from app.utils.web_utils import managed_session


class BaseParser(ABC):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
    }

    @abstractmethod
    def preprocess(self, session):
        pass

    @abstractmethod
    def process(self, session):
        pass

    def run(self):
        with managed_session() as session:
            self.preprocess(session)
            self.process(session)
