from typing import Optional
from pydantic import BaseModel, Field, validator

class HPAConfig(BaseModel):
    """Schema for HPA configuration"""
    min_replicas: int = Field(1, ge=1, description="Minimum number of replicas")
    max_replicas: int = Field(..., ge=1, description="Maximum number of replicas")
    target_cpu_utilization_percentage: Optional[int] = Field(
        None, ge=1, le=100,
        description="Target CPU utilization percentage"
    )
    target_memory_utilization_percentage: Optional[int] = Field(
        None, ge=1, le=100,
        description="Target memory utilization percentage"
    )

    @validator('max_replicas')
    def validate_max_replicas(cls, v, values):
        if 'min_replicas' in values and v < values['min_replicas']:
            raise ValueError("max_replicas must be greater than or equal to min_replicas")
        return v

    class Config:
        allow_population_by_field_name = True
