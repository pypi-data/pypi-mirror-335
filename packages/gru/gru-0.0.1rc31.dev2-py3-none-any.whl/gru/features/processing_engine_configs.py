from typing import Dict, Optional
from gru.utils.config_reader import ConfigReader
import re

class ProcessingEngineConfigs:
    """
    A class representing a feature retrieval service with a Processing Engine Configs.

    Args:
        config_path: A path to config file containing default parameters for processing engine

    Example:
        Initialize ProcessingEngineConfig:
        processing_engine_configs = ProcessingEngineConfigs(config_path="/path/to/config.yaml")
    """

    def __init__(
        self,
        deploy_mode: Optional[str] = "",
        driver_memory: Optional[str] = "",
        executor_memory: Optional[str] = "",
        service_account: Optional[str] = "",
        aws_credential_provider: Optional[str] = "",
        container_image: Optional[str] = "",
        container_image_pull_secrets: Optional[str] = "",
        file_upload_path: Optional[str] = "",
        name_space: Optional[str] = "",
        num_executors: Optional[int] = None,
        checkpoint_path: Optional[str] = None,
        executor_cores: Optional[int] = None,
        driver_cores: Optional[int] = None,
        driver_limit_cores: Optional[str] = "",
        executor_limit_cores: Optional[str] = "",
        executor_instances: Optional[int] = None,
        config_path: Optional[str] = None,
    ):
        self.deploy_mode = deploy_mode
        self.driver_memory = driver_memory
        self.executor_memory = executor_memory
        self.service_account = service_account
        self.aws_credential_provider = aws_credential_provider
        self.container_image = container_image
        self.container_image_pull_secrets = container_image_pull_secrets
        self.file_upload_path = file_upload_path
        self.name_space = name_space
        self.num_executors = num_executors
        self.executor_cores = executor_cores
        self.driver_cores = driver_cores
        self.driver_limit_cores = driver_limit_cores
        self.executor_limit_cores = executor_limit_cores
        self.executor_instances = executor_instances
        self.config = ConfigReader(config_path=config_path or getattr(self, 'default_config_path', None))
        self.checkpoint_path = checkpoint_path or self.config.checkpoint_path
        self._validate_checkpoint_path()

    def _validate_checkpoint_path(self):
        """
        Validates that the checkpoint path is a valid S3 path.

        Raises:
            ValueError: If the checkpoint path is not a valid S3 path.
        """
        if self.checkpoint_path:
            if not self.checkpoint_path.startswith('s3a://'):
                raise ValueError(f"Checkpoint path must start with 's3a://'. Got: {self.checkpoint_path}")

            # Split into bucket and key
            try:
                path = self.checkpoint_path[6:]  # Remove 's3a://'
                bucket = path.split('/')[0]

                # Basic bucket name validation
                if not bucket or not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket):
                    raise ValueError(f"Invalid S3 bucket name in checkpoint path: {bucket}")

            except Exception as e:
                raise ValueError(f"Invalid S3 path structure: {self.checkpoint_path}. Error: {str(e)}")


    def to_json(self) -> Dict:
        return {
            "deploy-mode": self.deploy_mode or self.config.deploy_mode,
            "spark.kubernetes.driver.memory": self.driver_memory
            or self.config.driver_memory,
            "spark.kubernetes.executor.memory": self.executor_memory
            or self.config.executor_memory,
            "spark.kubernetes.authenticate.driver.serviceAccountName": self.service_account
            or self.config.service_account,
            "spark.hadoop.fs.s3a.aws.credentials.provider": self.aws_credential_provider
            or self.config.aws_credential_provider,
            "spark.kubernetes.container.image": self.container_image
            or self.config.container_image,
            "spark.kubernetes.container.image.pullSecrets": self.container_image_pull_secrets
            or self.config.container_image_pull_secrets,
            "spark.kubernetes.file.upload.path": self.file_upload_path
            or self.config.file_upload_path,
            "spark.kubernetes.namespace": self.name_space or self.config.name_space,
            "num-executors": self.num_executors or self.config.num_executors,
            "checkpoint_path": self.checkpoint_path or self.config.checkpoint_path,
            "spark.executor.cores": self.executor_cores or self.config.executor_cores,
            "spark.driver.cores": self.driver_cores or self.config.driver_cores,
            "spark.kubernetes.driver.limit.cores": self.driver_limit_cores
            or self.config.driver_limit_cores,
            "spark.kubernetes.executor.limit.cores": self.executor_limit_cores
            or self.config.executor_limit_cores,
            "spark.executor.instances": self.executor_instances
            or self.config.executor_instances,
        }

class StreamingProcessingEngineConfigs(ProcessingEngineConfigs):
    """
    Processing Engine Configs for Streaming Features.
    """
    default_config_path = "./gru/config/features/default_processing_engine_configs_streaming.yaml"

class BatchProcessingEngineConfigs(ProcessingEngineConfigs):
    """
    Processing Engine Configs for Raw (Batch) Features.
    """
    default_config_path = "./gru/config/features/default_processing_engine_configs_batch.yaml"
