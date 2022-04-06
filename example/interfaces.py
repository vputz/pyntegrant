from abc import ABC, abstractmethod


class Input(ABC):
    @abstractmethod
    def get_input(self) -> str:
        ...


class Processor(ABC):
    @abstractmethod
    def process_input(self, s: str) -> dict:
        ...


class Output(ABC):
    @abstractmethod
    def format_output(self, d: dict) -> str:
        ...
