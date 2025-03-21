from typing import Optional, List
from gru.agents.framework_wrappers import BaseAgent
from langgraph.graph import StateGraph

from gru.agents.framework_wrappers.langgraph.workflow import LanggraphWorkflow
from gru.agents.memory.canso_memory import CansoMemory
from gru.agents.service.app import App
import logging
from gru.agents.clients.rabbitmq import RabbitMQPublisher
from gru.agents.utils.logging import RabbitMQLogHandler

class CansoLanggraphAgent(BaseAgent):
    def __init__(
        self, 
        stateGraph: StateGraph, 
        memory: Optional[CansoMemory] = None,
        interrupt_before: Optional[List[str]] = None,
    ) -> None:
        workflow = LanggraphWorkflow(stateGraph, interrupt_before)
        self.app = App(workflow, memory)
    
    def run(self):
        # self._setup_logging()
        self.app.run()
    
    def _setup_logging(self):
        try:
            rabbitmq_publisher = RabbitMQPublisher()
            rabbitmq_publisher.start()

            handler = RabbitMQLogHandler(rabbitmq_publisher)
            logging.getLogger().addHandler(handler)
        except Exception as e:
            print(f"Exception while initializing logging: {e}")
