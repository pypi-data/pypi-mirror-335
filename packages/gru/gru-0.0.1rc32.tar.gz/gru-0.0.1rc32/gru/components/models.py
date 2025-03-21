from pydantic import BaseModel

class Broker(BaseModel):
    type: str
    name: str

class CheckpointDB(BaseModel):
    type: str
    name: str
    size: str

class VectorDB(BaseModel):
    type: str
    name: str
    size: str
    image_pull_secret: str | None = None

class TaskServer(BaseModel):
    type: str
    name: str
    replicas: int
    concurrency_per_replica: int
    broker_name: str
    aws_role_arn: str | None = None

class ResourceSetupRequest(BaseModel):
    cluster_name: str = None
    broker: Broker = None
    checkpoint_db: CheckpointDB = None
    task_server: TaskServer = None
    vector_db: VectorDB = None