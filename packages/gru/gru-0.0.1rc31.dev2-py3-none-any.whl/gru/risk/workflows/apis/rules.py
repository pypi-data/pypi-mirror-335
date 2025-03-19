from typing import Any, Dict, List, Literal, Optional, Union
from gru import DEFAULT_CANSO_API_CONFIG
from gru.schema.api_request_handler import APIRequestHandler
from gru.schema.api_response_handler import APIResponseHandler
from gru.utils.config_reader import ConfigReader
from gru.risk.workflows.models.rules import CreateRuleRequest, RiskRule, UpdateRuleRequest, UpdateRuleStageRequest, UpdateRuleStatusRequest, WorkflowRulesQueryParams

def get_workflow_rules(
    auth_token: str,
    workflow_name: str,
    rule_name: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None
) -> List[RiskRule]:
    """
    Get rules for a workflow, optionally filtering by rule name, stage, and status.
    
    Args:
        auth_token: Authentication token
        workflow_name: Name of the workflow
        rule_name: Optional specific rule name to fetch
        stage: Optional stage filter
        status: Optional status filter
        
    Returns:
        List of RiskRule objects
        
    Raises:
        ApiError: If the API request fails
    """
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint) #TODO Temp fix
    
    endpoint = configs.workflow_rules_list_endpoint.replace(
        '{workflow-name}', 
        workflow_name
    )
    
    if rule_name:
        endpoint = f"{endpoint}/{rule_name}"
    else:
        params = WorkflowRulesQueryParams(stage=stage, status=status)
        request_handler.set_params(params.model_dump(exclude_none=True))
    
    response = request_handler.send_request("get", endpoint)
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    rules_data = response_handler.get_success_data()

    if isinstance(rules_data, list):
        return [RiskRule.model_validate(rule) for rule in rules_data]
    else:
        return [RiskRule.model_validate(rules_data)]
    

def create_rule(auth_token: str, workflow_name: str, rule_config: Dict[str, Any]) -> RiskRule:
    """
    Create a new rule for a workflow via the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        workflow_name: Name of the workflow to add the rule to
        rule_config: Rule configuration from JSON file
        
    Returns:
        RiskRule: The created rule object
        
    Raises:
        ApiError: If the API request fails
        ValueError: If rule configuration is invalid
    """
    rule_request = CreateRuleRequest.model_validate(rule_config)
    
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint)
    
    endpoint = configs.workflow_rules_create_endpoint.format(**{
        "workflow-name": workflow_name
    })
    
    response = request_handler.send_request(
        "post",
        endpoint,
        json_data=rule_request.model_dump(exclude_none=True)
    )
    
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    rule_data = response_handler.get_success_data()
    return RiskRule.model_validate(rule_data)

def update_workflow_rule(
    auth_token: str,
    workflow_name: str,
    rule_name: str,
    update_type: Literal['definition', 'status', 'stage'],
    request_data: Union[UpdateRuleRequest, UpdateRuleStatusRequest, UpdateRuleStageRequest]
) -> RiskRule:
    """
    Update a workflow rule via the Risk Workflow Management API.
    
    Args:
        auth_token: Authentication token
        workflow_name: Name of the workflow
        rule_name: Name of the rule to update
        update_type: Type of update (definition/status/stage)
        request_data: Request data for the update
        
    Returns:
        Updated RiskRule object
        
    Raises:
        ApiError: If the API request fails
    """
    configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
    request_handler = APIRequestHandler(auth_token, configs)
    request_handler.set_base_url(configs.risk_mgmt_endpoint) 
    endpoint_key = ''
    if update_type == 'definition':
        endpoint_key = 'update'
    elif update_type == 'status':
        endpoint_key = 'update_status'
    elif update_type == 'stage':
        endpoint_key = 'update_stage'
        
    endpoint = configs.risk_paths['rules'][endpoint_key]
    endpoint = endpoint.replace('{workflow-name}', workflow_name)
    endpoint = endpoint.replace('{rule-name}', rule_name)
    
    method = "put" if update_type == 'definition' else "patch"
    
    response = request_handler.send_request(
        method,
        endpoint,
        json_data=request_data.model_dump(exclude_none=True)
    )
    
    response_handler = APIResponseHandler(response)
    response_handler.check_for_errors()
    
    rule_data = response_handler.get_success_data()
    return RiskRule.model_validate(rule_data)
