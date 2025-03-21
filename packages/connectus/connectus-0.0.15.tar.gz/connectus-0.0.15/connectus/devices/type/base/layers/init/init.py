from abc import ABC, abstractmethod

class BaseInit(ABC):
    """
    Base class for initialization layers.
    """

    def __init__(self) -> None:
        """
        Initialize the base class.
        """
        super().__init__()

    @abstractmethod
    async def run(self) -> None:
        """
        Abstract method to run the initialization process.
        Must be implemented by subclasses.
        """
        pass