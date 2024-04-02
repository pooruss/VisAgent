from enum import Enum, unique
from colorama import Fore

@unique
class ActionType(Enum):
    Default = "default"
    OS = "os"
    WEB = "web"
    
    def __str__(self):
        return self.__class__.__name__ + ": " + self.name
    def color(self):
        return Fore.GREEN
            
@unique
class ActionStatusCode(Enum):
    FAILED = -1
    SUCCESS = 0
    FORMAT_ERROR = 1
    HALLUCINATE_NAME = 2 
    OTHER_ERROR = 3
    PENDING = 128
    
    def __str__(self):
        return self.__class__.__name__ + ": " + self.name
    def color(self):
        match self.name:
            case "SUCCESS":
                return Fore.GREEN
            case _:
                return Fore.RED
