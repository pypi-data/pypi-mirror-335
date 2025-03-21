from abc import ABC, abstractmethod

class Instrument(ABC):
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def initialize(self):
        """Initialize the instrument."""
        pass

    @abstractmethod
    def read(self):
        """Read data from the instrument."""
        pass

    @abstractmethod
    def write(self, command):
        """Send a command to the instrument."""
        pass

    @abstractmethod
    def shutdown(self):
        """Shut down or disconnect the instrument."""
        pass