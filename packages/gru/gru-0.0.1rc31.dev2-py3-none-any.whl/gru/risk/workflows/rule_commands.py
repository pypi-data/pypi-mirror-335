from typing import Any, Dict, List, Literal, Optional
from gru.cli import read_token
from gru.risk.workflows.utils import read_json_config
from gru.schema.api_response_handler import ApiError
from gru.risk.workflows.apis.rules import create_rule, get_workflow_rules, update_workflow_rule
from gru.risk.workflows.models.rules import RiskRule, UpdateRuleRequest, UpdateRuleStageRequest, UpdateRuleStatusRequest

class RulesCommands:
    """Commands for managing workflow rules"""
    
    def _format_sub_rules(self, rule_def: Dict[str, Any], indent: int = 2) -> List[str]:
        """Format sub-rules into readable lines"""
        lines = []
        spaces = " " * indent
        
        if "operator" not in rule_def or "sub_rules" not in rule_def:
            return lines
            
        lines.append(f"{spaces}Operator: {rule_def['operator']}")
        
        for sub_rule in rule_def.get("sub_rules", []):
            lines.append(f"{spaces}- Field: {sub_rule.get('field')}")
            lines.append(f"{spaces}  Operation: {sub_rule.get('operator')}")
            if sub_rule.get('value') is not None:
                lines.append(f"{spaces}  Value: {sub_rule['value']}")
            if sub_rule.get('redis_key'):
                lines.append(f"{spaces}  Redis Key: {sub_rule['redis_key']}")
            if sub_rule.get('redis_field'):
                lines.append(f"{spaces}  Redis Field: {sub_rule['redis_field']}")
                
        return lines
    
    def _format_rule(self, rule: RiskRule, detailed: bool = False) -> List[str]:
        """Format a rule into a list of output lines"""
        lines = []
        
        # Basic info
        status_str = f"[{rule.status}]"
        stage_str = f"(Stage: {rule.stage})"
        lines.append(f"{rule.rule_name} {status_str} {stage_str}")
        
        # Add rule definition details if requested
        if detailed:
            lines.extend(self._format_sub_rules(rule.rule_definition))
            lines.append(f"Created: {rule.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            lines.append(f"Updated: {rule.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            lines.append("")
            
        return lines

    def list(
        self,
        workflow_name: str,
        rule_name: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        detailed: bool = False
    ) -> str:
        """
        List rules for a workflow or get details of a specific rule.
        
        Args:
            workflow_name: Name of the workflow
            rule_name: Optional specific rule to retrieve
            stage: Optional stage filter
            status: Optional status filter
            detailed: Whether to show detailed rule information
            
        Returns:
            Formatted string containing rule information
        """
        try:
            auth_token = read_token()
            
            rules = get_workflow_rules(
                auth_token, 
                workflow_name,
                rule_name,
                stage,
                status
            )
            
            if not rules:
                return "No rules found"
            
            output_lines = []
            
            if rule_name:

                output_lines.append(f"Rule details for '{rule_name}':")
            else:

                filters = []
                if stage:
                    filters.append(f"stage={stage}")
                if status:
                    filters.append(f"status={status}")
                    
                header = f"Rules for workflow '{workflow_name}'"
                if filters:
                    header += f" (Filters: {', '.join(filters)})"
                output_lines.append(header)
            
            output_lines.append("")

            for rule in rules:
                output_lines.extend(
                    self._format_rule(rule, detailed=detailed or rule_name is not None)
                )
            
            return "\n".join(output_lines).rstrip()
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return str(value_error)
        except Exception as e:
            return f"Error: {str(e)}"
        
    def create(self, workflow_name: str, config: str) -> str:
        """
        Create a new rule for a workflow using configuration from a JSON file.
        
        Args:
            workflow_name: Name of the workflow to add the rule to
            config: Path to JSON configuration file
            
        Returns:
            Formatted string with created rule details or error message
        """
        try:
            auth_token = read_token()
            rule_config = read_json_config(config)
                
            rule = create_rule(auth_token, workflow_name, rule_config)
            
            return (
                f"Successfully created rule in workflow '{workflow_name}':\n\n"
                f"{self._format_rule(rule)}"
            )
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return str(value_error)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def update(
        self,
        workflow_name: str,
        rule_name: str,
        config: Optional[str] = None,
        status: Optional[Literal['ACTIVE', 'INACTIVE', 'DEPRECATED']] = None,
        stage: Optional[Literal['REGISTERED', 'BACKTESTING', 'STAGING', 'PRODEXPERIMENT', 'LIVE']] = None
    ) -> str:
        """
        Update a workflow rule's definition, status, or stage.
        
        Args:
            workflow_name: Name of the workflow
            rule_name: Name of the rule to update
            config: Optional path to rule definition JSON file
            status: Optional new status value
            stage: Optional new stage value
            
        Returns:
            Formatted string showing updated rule details
            
        Note: Exactly one of config, status, or stage must be provided
        """
        try:
            # Validate input combination
            provided_options = sum(bool(x) for x in [config, status, stage])
            if provided_options != 1:
                return "Error: Exactly one of --config, --status, or --stage must be provided"
            
            auth_token = read_token()
            
            if config:
                config_data = read_json_config(config)
                request = UpdateRuleRequest.model_validate(config_data)
                update_type = 'definition'
                request_data = request
            elif status:
                request = UpdateRuleStatusRequest(new_status=status)
                update_type = 'status'
                request_data = request
            elif stage:  
                request = UpdateRuleStageRequest(stage=stage)
                update_type = 'stage'
                request_data = request
            
            updated_rule = update_workflow_rule(
                auth_token,
                workflow_name,
                rule_name,
                update_type,
                request_data
            )
            
            update_type_str = 'definition' if config else 'status' if status else 'stage'
            return "\n".join([
                f"Successfully updated rule {update_type_str}:",
                "",
                *self._format_rule(updated_rule, detailed=True)
            ])
            
        except ApiError as api_error:
            return f"API Error: {api_error.message}"
        except ValueError as value_error:
            return f"Validation error: {str(value_error)}"
        except Exception as e:
            return f"Error: {str(e)}"

