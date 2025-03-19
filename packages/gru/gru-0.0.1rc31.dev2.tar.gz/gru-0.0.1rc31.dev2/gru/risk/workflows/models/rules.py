from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel


class WorkflowRulesQueryParams(BaseModel):
    """Query parameters for listing workflow rules"""
    stage: Optional[str] = None
    status: Optional[str] = None

class RiskRule(BaseModel):
    """Schema for rule response"""
    rule_name: str
    rule_definition: Dict[str, Any]  # Contains operator and sub_rules
    stage: Literal['REGISTERED', 'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE']
    status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']
    created_at: datetime
    updated_at: datetime

class SubRule(BaseModel):
    field: str
    operator: Literal['<', '>', '==', '!=', '>=', '<=']
    value: Optional[Any] = None
    redis_key: Optional[str] = None
    redis_field: Optional[str] = None


class BaseRuleRequest(BaseModel):
    """Base model for rule requests"""
    operator: Literal['AND', 'OR']
    sub_rules: List[SubRule]

class CreateRuleRequest(BaseRuleRequest):
    """Model for creating a new rule"""
    rule_name: str

class UpdateRuleRequest(BaseRuleRequest):
    """Model for updating an existing rule"""
    pass

class UpdateRuleStatusRequest(BaseModel):
    """Request model for updating Rule status"""
    new_status: Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']

class UpdateRuleStageRequest(BaseModel):
    """Request model for updating Rule stage"""
    stage: Literal['REGISTERED', 'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE']

    @classmethod
    def from_str(cls, stage: str) -> 'UpdateRuleStageRequest':
        """
        Create request from string status, with validation
        """
        stage_upper = stage.upper()
        if stage_upper not in ('REGISTERED', 'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE'):
            raise ValueError(
                "Stage must be one of:'REGISTERED', 'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE'"
            )
        return cls(stage=stage_upper) 

