from agent.model import Model
from agent.printer import ModelPrinterListener
from agent.session import Session
from agent.tool import registry
from agent.listener import ModelListener


class Agent:

    def __init__(
        self,
        *,
        session: Session | None = None,
        model: Model | None = None,
        model_listener: ModelListener | None = None,
    ) -> None:
        self.session = session or Session()
        self.model = model or Model()
        self.listener = model_listener
        if self.listener:
            self.listener.listen(self.model)

    def invoke(self, q: str):
        self.session.add_message({"role": "user", "content": q})
        responses = []
        # ReAct Loop
        while True:
            resp = self.model.invoke_stream(self.session)
            call_msg = registry.invoke(self.session.messages[-1])
            if call_msg is None:
                responses.append(resp)
                break
            else:
                self.session.messages += call_msg
                responses.append(resp)
        return responses
