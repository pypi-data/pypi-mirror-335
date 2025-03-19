from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel
from gru.schema.api_response_handler import ApiError
from gru.risk.workflows.apis.workflows import create_workflow, deploy_workflow, get_workflow, get_workflows, update_workflow_status
from gru.risk.workflows.models.workflows import (
    CreateWorkflowWithRuleRequest, 
    RuleDetails, 
    UpdateWorkflowStatusResponse, 
    Workflow, 
    WorkflowDeployment, 
    WorkflowDetails
)
from gru.risk.workflows.rule_commands import RulesCommands
from gru.risk.workflows.utils import read_json_config
from gru.cli import read_token
from gru.utils.config_reader import ConfigReader

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp to a readable string"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

class WorkflowCommands(object):

    def __init__(self):
        self.rules = RulesCommands()

    def _format_workflow_deployment(self, deploy: WorkflowDeployment) -> str:
        """Format a single workflow deployment"""
        cluster = deploy.cluster_name
        status = deploy.deployment_status
        last_synced = format_timestamp(deploy.last_synced_at) if deploy.last_synced_at else 'Never'
        return f" - {cluster}: {status} (Last synced: {last_synced})"

    def _format_workflow(self, workflow: Union[Workflow, UpdateWorkflowStatusResponse]) -> List[str]:
        """Format a workflow into a list of output lines"""
        output_lines = []
        
        status_str = f"[{workflow.status}]" if workflow.status else ""
        desc_str = f": {workflow.description}" if workflow.description else ""

        deploy_str = ""

        if hasattr(workflow, 'deployments') and workflow.deployments:
            deploys = len(workflow.deployments)
            deploy_str = f" ({deploys} deployment{'s' if deploys != 1 else ''})"
        
        output_lines.append(
            f"{workflow.workflow_name} {status_str}{desc_str}{deploy_str}"
        )

        if hasattr(workflow, 'deployments') and workflow.deployments:
            output_lines.append(" Deployments:")
            for deploy in workflow.deployments:
                output_lines.append(self._format_workflow_deployment(deploy))
            output_lines.append("")  
            
        return output_lines

    def _format_rule(self, rule: RuleDetails) -> List[str]:
        """Format a single rule into a list of output lines"""
        output_lines = []
        output_lines.append(f" - {rule.rule_name} [{rule.status}] (Stage: {rule.stage})")
        return output_lines

    def _format_workflow_detailed(self, workflow: WorkflowDetails) -> List[str]:
        """Format a workflow with rules into a list of output lines"""
        output_lines = self._format_workflow(workflow)
        
        if workflow.rules:
            output_lines.append(" Rules:")
            for rule in workflow.rules:
                output_lines.extend(self._format_rule(rule))
        
        return output_lines
    
    def _format_model_response(self, response: BaseModel) -> str:
        """Format a model response into a string"""
        return "\n".join(f"  {k}: {v}" for k, v in response.model_dump().items())

    def list(
    self, 
    workflow_name: Optional[str] = None, 
    is_active: Optional[bool] = None,
    detailed: bool = False
    ) -> str:
        """
        List workflows or get details of a specific workflow.
        
        Args:
            workflow_name: Optional name of specific workflow to retrieve
            is_active: Optional filter for active/inactive workflows
            detailed: Whether to show detailed information including rules
            
        Returns:
            Formatted string containing workflow information
        """
        try:
            auth_token = read_token()
            
            if workflow_name:
                workflow = get_workflow(auth_token, workflow_name)
                return "\n".join(self._format_workflow_detailed(workflow))
            

            workflows = get_workflows(auth_token, is_active)
            if not workflows:
                return "No workflows found"
            
            output_lines = []
            for workflow in workflows:
                if detailed:
                    detailed_workflow = get_workflow(auth_token, workflow.workflow_name)
                    output_lines.extend(self._format_workflow_detailed(detailed_workflow))
                else:
                    output_lines.extend(self._format_workflow(workflow))
                
            return "\n".join(output_lines).rstrip()
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return str(value_error)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create(self, workflow_name: str, config: str) -> str:
        """
        Create a new workflow using configuration from JSON file.
        
        Args:
            workflow_name: Name for the new workflow
            config: Path to JSON configuration file
            
        Returns:
            Formatted string showing created workflow details
        """
        try:
            auth_token = read_token()
            
            config_data = read_json_config(config)
            
            config_data["workflow_name"] = workflow_name
            
            request = CreateWorkflowWithRuleRequest.model_validate(config_data)
            
            workflow = create_workflow(auth_token, request)
            
            return "\n".join([
                f"Successfully created workflow: {workflow_name}",
                "",
                *self._format_workflow_detailed(workflow)
            ])
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return f"Configuration error: {str(value_error)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def update_status(self, workflow_name: str, status: str) -> str:
        """
        Update the status of a workflow.
        
        Args:
            workflow_name: Name of the workflow to update
            status: New status ('ACTIVE', 'INACTIVE', or 'DEPRECATED')
            
        Returns:
            Formatted string showing updated workflow details
        """
        try:
            auth_token = read_token()
            
            workflow = update_workflow_status(auth_token, workflow_name, status)
            
            return "\n".join([
                f"Successfully updated workflow status:",
                "",
                *self._format_workflow(workflow)
            ])
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return f"Invalid status: {str(value_error)}"
        except Exception as e:
            return f"Error: {str(e)}"
        
    def deploy(
    self,
    workflow_name: str,
    env: str,
    cluster_name: str,
    namespace: str,
    env_vars: str = "",
    hpa_configs: Optional[str] = None
    ) -> str:
        """
        Deploy a workflow to the specified environment.
        
        Args:
            workflow_name: Name of the workflow to deploy
            env: Target environment (STAGING/PRODEXPERIMENT/LIVE)
            cluster_name: Name of the target cluster
            namespace: Kubernetes namespace
            env_vars: Optional environment variables in format "key1=value1,key2=value2"
            hpa_configs: Optional path to HPA configuration file (YAML/JSON)
            
        Returns:
            Formatted string showing deployment result
        """
        try:
            auth_token = read_token()
            
            env_vars_dict = {}
            if env_vars:
                try:
                    env_vars_dict = dict(
                        pair.split('=', 1) 
                        for pair in env_vars.split(',')
                    )
                except ValueError:
                    return "Error: env_vars must be in format 'key1=value1,key2=value2'"
            
            hpa_config = ConfigReader.load_hpa_config(hpa_configs)

            env = env.upper()
            if env not in ["BACKTESTING", "STAGING", "PRODEXPERIMENT", "LIVE"]:
                return "Error: env must be one of: BACKTESTING, STAGING, PRODEXPERIMENT, LIVE"
            
            response = deploy_workflow(
                auth_token,
                workflow_name,
                cluster_name,
                env,
                namespace,
                env_vars_dict,
                hpa_config
            )
            
            return "\n".join([
                f"Successfully queued workflow deployment:",
                "",
                f"Details: ",
                self._format_model_response(response)
            ])
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return f"Invalid input: {str(value_error)}"
        except Exception as e:
            return f"Error: {str(e)}"


