from gru.risk.workflows.workflow_commands import WorkflowCommands
import fire

class CansoCommands:
    """Root command class for the Canso CLI"""
    
    def __init__(self):
        self.workflows = WorkflowCommands()

def main():
    fire.Fire(CansoCommands)
