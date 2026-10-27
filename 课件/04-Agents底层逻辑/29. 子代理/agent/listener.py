from abc import ABC, abstractmethod

from agent.model import Model
from agent.events import Event


class ModelListener(ABC):

    def __init__(self) -> None:
        self.listening = True

    def listen(self, model):
        events = [v for k, v in Event.__dict__.items() if not k.startswith("__")]
        for e in events:
            model.on(event=e, callback=self._model_print_callback)

    def _model_print_callback(self, e: str, **args):
        if not self.listening:
            return
        self._handler(e, **args)

    @abstractmethod
    def _handler(self, e: str, **args):
        pass
