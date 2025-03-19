from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel
from gru.models.common.hpa_config import HPAConfig

class WorkflowListQueryParams(BaseModel):
    """Query parameters for listing workflows"""    
    is_active: Optional[bool] = None

class WorkflowDeployment(BaseModel):
    """Schema for workflow deployment details"""
    cluster_name: str
    deployment_status: Literal['PENDING', 'DEPLOYED', 'FAILED', 'TERMINATED']
    last_synced_at: Optional[datetime]

class Workflow(BaseModel):
    """Schema for workflow response"""
    workflow_name: str
    description: Optional[str]
    status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']
    deployments: List[WorkflowDeployment]
    created_at: datetime
    updated_at: datetime

class RuleDetails(BaseModel):
    """Schema for rule details within a workflow"""
    rule_name: str
    rule_definition: Dict[str, Any]
    stage: Literal['REGISTERED', 'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE']
    status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']
    created_at: datetime
    updated_at: datetime

class WorkflowDetails(BaseModel):
    """Schema for detailed workflow response including rules"""
    workflow_name: str
    description: Optional[str]
    status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']
    rules: List[RuleDetails]
    deployments: List[WorkflowDeployment]
    created_at: datetime
    updated_at: datetime

class SubRule(BaseModel):
    field: str
    operator: Literal['<', '>', '==', '!=', '>=', '<=']
    value: Optional[Any] = None 
    storage_key: Optional[str] = None
    storage_field: Optional[str] = None

class CreateRuleRequest(BaseModel):
    rule_name: str
    operator: Literal['AND', 'OR']
    sub_rules: List[SubRule]

class CreateWorkflowWithRuleRequest(BaseModel):
    """Request model for creating a new workflow with initial rules"""
    workflow_name: str
    description: Optional[str]
    initial_rules: List[CreateRuleRequest] 

class UpdateWorkflowStatusRequest(BaseModel):
    """Schema for workflow status update request"""
    new_status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']

    @classmethod
    def from_str(cls, status: str) -> 'UpdateWorkflowStatusRequest':
        """
        Create request from string status, with validation
        """
        status_upper = status.upper()
        if status_upper not in ('ACTIVE', 'INACTIVE', 'DEPRECATED'):
            raise ValueError(
                "Status must be one of: ACTIVE, INACTIVE, DEPRECATED"
            )
        return cls(new_status=status_upper) 

class UpdateWorkflowStatusResponse(BaseModel):
    """Response model for workflow status update"""
    workflow_name: str
    description: Optional[str]
    status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']
    created_at: datetime
    updated_at: datetime

class DeployWorkflowRequest(BaseModel):
    """Request model for workflow deployment"""
    cluster_name: str
    environment: Literal["BACKTESTING", "STAGING", "PRODEXPERIMENT", "LIVE"]
    namespace: str
    env_vars: Dict[str, str] = {}
    hpa_configs: Optional[HPAConfig] = None

    class Config:
        allow_population_by_field_name = True

class DeployWorkflowResponse(BaseModel):
    """Response model for workflow deployment"""
    
    deployment_strategy: str
    deployment_id: str
    workflow_name: str
    environment: str
    argocd_app_name: str
    namespace: str
    chart: Optional[str] = None
    version: Optional[str] = None