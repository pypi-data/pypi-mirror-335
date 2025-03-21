from typing import Dict, List, Optional
from gru import DEFAULT_CANSO_API_CONFIG
from gru.schema.api_request_handler import APIRequestHandler
from gru.schema.api_response_handler import APIResponseHandler
from gru.utils.config_reader import ConfigReader
from gru.risk.workflows.models.workflows import (
    CreateWorkflowWithRuleRequest, 
    DeployWorkflowRequest, 
    DeployWorkflowResponse, 
    UpdateWorkflowStatusRequest, 
    UpdateWorkflowStatusResponse, 
    Workflow, 
    WorkflowDetails, 
    WorkflowListQueryParams,
    HPAConfig,
)

def get_workflows(auth_token: str, is_active: Optional[bool] = None) -> List[Workflow]:
    """
    Get all workflows via the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        is_active: Optional filter for active/inactive workflows
        
    Returns:
        List of Workflow objects
        
    Raises:
        ApiError: If the API request fails
    """
    # Create query params if needed
    params = {}

    if is_active is not None:
        params["is_active"] = is_active
        
    query_params = WorkflowListQueryParams(**params)
    
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint)
    
    request_handler.set_params(query_params.model_dump(exclude_none=True))

    response = request_handler.send_request(
        "get", 
        configs.workflow_list_endpoint,
    )
    

    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    workflows_data = response_handler.get_success_data()
    return [Workflow.model_validate(wf) for wf in workflows_data]

def get_workflow(auth_token: str, workflow_name: str) -> WorkflowDetails:
    """
    Get detailed workflow information by name from the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        workflow_name: Name of the workflow to retrieve
        
    Returns:
        WorkflowDetails object with complete workflow information
        
    Raises:
        ApiError: If the API request fails
    """
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint)

    endpoint = configs.workflow_get_endpoint.replace('{workflow-name}', workflow_name)
    
    response = request_handler.send_request("get", endpoint)
    
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    workflow_data = response_handler.get_success_data()
    return WorkflowDetails.model_validate(workflow_data)

def create_workflow(auth_token: str, request: CreateWorkflowWithRuleRequest) -> WorkflowDetails:
    """
    Create a new workflow via the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        request: CreateWorkflowRequest containing workflow configuration
        
    Returns:
        WorkflowDetails of created workflow
        
    Raises:
        ApiError: If the API request fails
    """
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint)

    response = request_handler.send_request(
        "post",
        configs.workflow_create_endpoint,
        json_data=request.model_dump(exclude_none=True)
    )
    
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    workflow_data = response_handler.get_success_data()
    return WorkflowDetails.model_validate(workflow_data)

def update_workflow_status(auth_token: str, workflow_name: str, status: str) -> UpdateWorkflowStatusResponse:
    """
    Update workflow status via the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        workflow_name: Name of the workflow to update
        status: New status string (will be validated)
        
    Returns:
        Updated Workflow object
        
    Raises:
        ApiError: If the API request fails
        ValueError: If status is invalid
    """
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint)

    endpoint = configs.workflow_update_status_endpoint.replace('{workflow-name}', workflow_name)
    
    request_data = UpdateWorkflowStatusRequest.from_str(status)
    
    response = request_handler.send_request(
        "patch",
        endpoint,
        json_data=request_data.model_dump()
    )
    
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    workflow_data = response_handler.get_success_data()

    return UpdateWorkflowStatusResponse.model_validate(workflow_data)

def deploy_workflow(
    auth_token: str, 
    workflow_name: str,
    cluster_name: str,
    environment: str,
    namespace: str,
    env_vars: Optional[Dict[str, str]] = None,
    hpa_config: Optional[HPAConfig] = None,
) -> DeployWorkflowResponse:
    """
    Deploy a workflow to specified environment via the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        workflow_name: Name of the workflow to deploy
        cluster_name: Name of the target cluster
        environment: Target environment (STAGING/PRODEXPERIMENT/LIVE)
        namespace: Kubernetes namespace
        env_vars: Optional environment variables for deployment
        hpa_config: Optional HPAConfig object for horizontal pod autoscaling
        
    Returns:
        Deployment response object
        
    Raises:
        ApiError: If the API request fails
        ValueError: If environment is invalid
    """
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint)
    
    endpoint = configs.workflow_deploy_endpoint.replace('{workflow-name}', workflow_name)
    
    allowed_environments = {'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE'}
    if environment.upper() not in allowed_environments:
        raise ValueError(f"Invalid environment: {environment}. Must be one of {allowed_environments}.")

    request_data = DeployWorkflowRequest(
        cluster_name=cluster_name,
        environment=environment.upper(), 
        namespace=namespace,
        env_vars=env_vars or {},
        hpa_configs=hpa_config
    )
    
    response = request_handler.send_request(
        "post",
        endpoint,
        json_data=request_data.model_dump(exclude_none=True)
    )
    
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    deployment_data = response_handler.get_success_data()
    return DeployWorkflowResponse.model_validate(deployment_data)

