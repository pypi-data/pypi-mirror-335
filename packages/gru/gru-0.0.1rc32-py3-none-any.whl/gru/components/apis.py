import yaml
from gru import DEFAULT_CANSO_API_CONFIG
from gru.components.models import ResourceSetupRequest
from gru.schema.api_request_handler import APIRequestHandler
from gru.schema.api_response_handler import APIResponseHandler
from gru.utils.config_reader import ConfigReader

def setup(correlation_id:str, cluster_name: str, config_file:str, auth_token: str):
    
        with open(config_file, "r") as config_file:
            config_dict = yaml.safe_load(config_file)

        resource_setup_request = ResourceSetupRequest(**config_dict)
        resource_setup_request.cluster_name = cluster_name
        request_json = resource_setup_request.model_dump()

        configs = ConfigReader(DEFAULT_CANSO_API_CONFIG)
        request_handler = APIRequestHandler(auth_token, configs, base_url=configs.agents_service_url)
        request_handler.set_correlation_id(correlation_id)
        response = request_handler.send_request("post", configs.component_setup_endpoint, request_json)
        response_handler = APIResponseHandler(response)

        return response_handler.get_message()