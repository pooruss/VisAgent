import abc
from VAgent.models import EnvState, Action
from VAgent.config import CONFIG
from VAgent.environment.base import BaseEnvironment
from VAgent.memory import BaseMemory

class BaseEngine(metaclass=abc.ABCMeta):
    def __init__(self, config: CONFIG):
        super().__init__()
        self.config = config

    @abc.abstractmethod
    def run(self, task: str, env: BaseEnvironment, memory: BaseMemory=None) -> EnvState:
        """Execute the engine and return the result env."""
        raise NotImplementedError