import abc
from VAgent.models import Action
from VAgent.config import CONFIG

class BaseAgent(metaclass=abc.ABCMeta):
    def __init__(self, config: CONFIG):
        super().__init__()
        self.config = config

    @abc.abstractmethod
    def predict(self,) -> Action:
        """Predict and return the result."""
        raise NotImplementedError
