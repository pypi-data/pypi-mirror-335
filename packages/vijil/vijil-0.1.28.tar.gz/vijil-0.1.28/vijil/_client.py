import os
import uuid
import pandas as pd
import json
from typing import List, Optional, Any, Dict
from dataclasses import field
from datetime import datetime, timezone
import jinja2
from fpdf import FPDF
import hashlib
import base64
import requests

from vijil.api import make_api_request, get_api_proxy_dict, BASE_URL, SUPPORTED_HUBS, DEFAULT_DETECTOR_PARAMS, DETECTOR_LIST
from vijil.types import VijilClient
from vijil.utils import calculate_md5_base64

ERROR_SKIP_KEYS = ['ERROR', 'SKIP']
HUB_CONFIG_FIELDS = {
    "vertex": ["region", "project_id", "client_id", "client_secret", "refresh_token"],
    "digitalocean": ["agent_id","agent_key"]
}
HUBS_NEEDING_URL = ["custom", "bedrock_custom", "azure", "digitalocean"]
HUBS_NOT_NEEDING_MODEL_NAME = ["digitalocean"]
OBJECTS_VERSION="1.2.31"

def modify_hub(model_hub: str):
    
    if model_hub == "bedrock":
        return "bedrock_custom"
    return model_hub

class APIKeys:
    """
    Class for managing model hub API keys, which are required to query models.

    :param client: The Vijil client instance.
    :type client: VijilClient
    """
    
    def __init__(self, client: VijilClient) -> None:
        """Constructor class

        :param client: The Vijil client instance.
        :type client: VijilClient
        """
        self.endpoint = "api-keys"
        self.client = client
        pass
    
    def list(self):
        """List all stored model hub API keys.

        :return: List of dictionaries. Each dictionary contains information about an API key.
        :rtype: List(dict)
        """
        response = make_api_request(base_url=self.client.base_url, endpoint=self.endpoint, token=self.client.api_key)
        return response
    
    def get_id_by_name(self, name: str):
        """ Get the id of a key by its name. Used by other functions to get the id of a key to modify.

        :param name: The name of the key.
        :type name: str
        :return: The id of the key.
        :rtype: str
        """

        if not self.name_exists(name):
            raise ValueError(f"Key '{name}' does not exist. Please specify an existing name.")

        #get id of key to modify
        response = self.list()
        return [item['id'] for item in response if item['name'] == name][0]
    
    def check_model_hub(self, model_hub: str):
        """Used by other functions to check that the model hub is valid and the key name is unique

        :param model_hub: The name of the model hub.
        :type model_hub: str
        :raises ValueError: If the model hub is not supported.
        """
        
        model_hub = modify_hub(model_hub)

        # check if model_hub is valid
        if (model_hub is not None) and (model_hub not in SUPPORTED_HUBS.keys()):
            raise ValueError(f"Model hub {model_hub} is not supported.")
    
    def name_exists(self, name: str):
        """Check whether the API key name already exists. Some functions need it to be exist, others need it to not exist.
        
        :param name: The name of the key.
        :type name: str
        :return: True if the name exists among the stored API keys, False otherwise.
        :rtype: bool
        """
        
        response = self.list()
        if response is not None and name in [item['name'] for item in response]:
            return True
        else:
            return False

    def create(self, name: str, model_hub: str, rate_limit_per_interval: int=60, rate_limit_interval: int=10, api_key: Optional[str]=None, hub_config: Optional[dict[Any, Any]]=None):
        """Create a new model hub API key.

        :param name: Name for the API key. This must be unique.
        :type name: str
        :param model_hub: Name of the model hub. Current supported values are 'openai', 'together', 'octo'.
        :type model_hub: str
        :param rate_limit_per_interval: The maximum amount of times Vijil will query the model hub in the specified rate_limit_interval, defaults to 60
        :type rate_limit_per_interval: int, optional
        :param rate_limit_interval: The size of the interval (in seconds) defining maximum queries to model hub in said interval. For example, if rate_limit_per_interval is 60 and rate_limit_interval is 10, then Vijil will query the model hub at most 60 times in 10 seconds. Defaults to 10
        :type rate_limit_interval: int, optional
        :raises ValueError: If you try to create a key with a name that belongs to an existing key.
        :return: Response to the API request.
        :rtype: dict
        :param api_key: The API key.
        :type api_key: str, optional
        :param hub_config: A dictionary containing additional configuration for the model hub. Defaults to None.
        :type hub_config: dict, optional
        """
        # conditional checks for fields
        model_hub = modify_hub(model_hub)
        
        # hub name     
        self.check_model_hub(model_hub=model_hub)

        # api key name
        if self.name_exists(name):
            raise ValueError(f"Key name '{name}' already exists. Please specify a different name.")
        
        # hub config and api key for vertex
        if model_hub in HUB_CONFIG_FIELDS.keys():
            api_key = ""
            if hub_config is None or not all([field in hub_config for field in HUB_CONFIG_FIELDS[model_hub]]):
                raise ValueError(f"Please provide the following fields in the hub_config for {SUPPORTED_HUBS[model_hub]}: {HUB_CONFIG_FIELDS[model_hub]}")
        else:
            if hub_config is not None:
                raise ValueError(f"Hub config is only needed for {SUPPORTED_HUBS[model_hub]}. Please remove it for other model hubs.")
            if api_key is None:
                raise ValueError("Please provide an API key.")

        # construct the payload
        payload = {
            "name": name,
            "hub": model_hub,
            "rate_limit_per_interval": rate_limit_per_interval,
            "rate_limit_interval": rate_limit_interval,
            "value": api_key,
        }
        if hub_config:
            payload["hub_config"] = hub_config
        
        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint,
            method="post",
            data=payload,
            token=self.client.api_key
        )
    
    def rename(self, name: str, new_name: str):
        """Rename a stored API key
        
        :param name: The current name of the key.
        :type name: str
        :param new_name: The new name of the key.
        :type new_name: str
        """

        key_id = self.get_id_by_name(name=name)
        
        payload = {
            "name": new_name
        }

        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint + "/" + key_id,
            method="put",
            data=payload,
            token=self.client.api_key
        )

    
    def modify(self, name: str, model_hub: str, api_key:Optional[str] = None, rate_limit_per_interval=None, rate_limit_interval=None):
        """Modify model hub, key, or rate limits of a stored API key. Cannot be used to rename key.
        
        :param name: The name of the key you want to modify.
        :type name: str
        :param model_hub: Name of the model hub. Current supported values are 'openai', 'together', 'octo'.
        :type model_hub: str, optional
        :param api_key: The API key.
        :type api_key: str, optional
        :param rate_limit_per_interval: The maximum amount of times Vijil will query the model hub in the specified rate_limit_interval, defaults to 60
        :type rate_limit_per_interval: int, optional
        :param rate_limit_interval: The size of the interval (in seconds) defining maximum queries to model hub in said interval. For example, if rate_limit_per_interval is 60 and rate_limit_interval is 10, then Vijil will query the model hub at most 60 times in 10 seconds. Defaults to 10
        :type rate_limit_interval: int, optional
        """

        #check that model hub is supported and key name refers to existing name
        self.check_model_hub(model_hub=model_hub)        
        
        key_id = self.get_id_by_name(name=name)

        payload = {
            "name": name,
            "hub": model_hub,
            "rate_limit_per_interval": rate_limit_per_interval,
            "rate_limit_interval": rate_limit_interval,
            "value": api_key,
        }

        #remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint + "/" + key_id,
            method="put",
            data=payload,
            token=self.client.api_key
        )

    def delete(self, name: str):
        """Delete API key with specified name
        
        :param name: The name of the key you want to delete
        :type name: str
        :return: Response to the API request.
        :rtype: dict
        """

        key_id = self.get_id_by_name(name=name)

        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint + "/" + key_id,
            method="delete",
            token=self.client.api_key
        )


class Harnesses:
    """Class for handling harnesses API requests.
    
    :param client: The VijilClient instance.
    :type client: VijilClient
    """
    
    def __init__(self, client: VijilClient) -> None:
        """Initialize the Harnesses class.

        :param VijilClient client: The VijilClient instance.
        :type client: VijilClient
        """
        self.endpoint = "harness-configs"
        self.client = client
        pass

    def calculate_md5_base64(self, file_path: str) -> str:
        with open(file_path, "rb") as file:
            md5_hash = hashlib.md5(file.read()).digest()
            return base64.b64encode(md5_hash).decode()

    def calculate_file_size(self, file_path):
        return os.path.getsize(file_path)

    def list(self):
        """List all harnesses.

        :return: List of dicts where each dict contains the metadata for a harness.
        :rtype: List(dict)
        """
        response = make_api_request(base_url=self.client.base_url, endpoint=self.endpoint, token=self.client.api_key)
        return response["results"]
    
    def create(self, name: str, system_prompt: str, category: List[str], policy_file_path: Optional[str] = None, kb_bucket: Optional[str] = None, input_schema: Optional[Dict[str, Any]]={}, output_schema: Optional[Dict[str, Any]]={}, function_route: Optional[str]=""):
        """
        Create a custom harness from a system prompt and file.
        
        :param name: The name of the harness.
        :param system_prompt: The system prompt for the model you're testing.
        :param category: The category of the harness. Options are "AGENT_POLICY", "KNOWLEDGE_BASE", "FUNCTION_ROUTE"
        :param policy_file_path: The path to the policy document (pdf or txt). Applicable to an agent policy harness. Defaults to "".
        :param kb_bucket: The bucket name for the knowledge base. Must be specified if you want to include a knowledge base harness. Defaults to "".
        :param input_schema: The input schema to be used for harness creation. Applicable to a tool-calling agent. Defaults to {}.
        :param output_schema: The output schema to be used for harness creation. Applicable to a tool-calling agent. Defaults to {}.
        :param function_route: The function route to be used for harness creation. Applicable to a tool-calling agent. Defaults to "".
        """
        # initial validation
        if "AGENT_POLICY" in category and (not policy_file_path) and not(system_prompt):
            raise ValueError("For AGENT_POLICY category, policy_file_path or system_prompt must be specified.")
        elif "FUNCTION_ROUTE" in category and (
            not function_route or not input_schema or not output_schema
        ):
            raise ValueError("For FUNCTION_ROUTE category, function_route must be specified and input_schema and output_schema must be empty.")
        elif "KNOWLEDGE_BASE" in category: 
            if not kb_bucket:
                raise ValueError("For KNOWLEDGE_BASE category, kb_bucket must be specified.")
        elif "AGENT_POLICY" not in category and "KNOWLEDGE_BASE" not in category and "FUNCTION_ROUTE" not in category:
            raise ValueError("Invalid category. Category must be 'AGENT_POLICY', 'KNOWLEDGE_BASE', or 'FUNCTION_ROUTE'.")
        
        # step 1: staging api call
        harness_config_id = str(uuid.uuid4())
        staging_payload = {
            "harness_config_version": "1.0.X",
            "harness_name": name,
            "agent_system_prompt": system_prompt,
        }
        try:
            staging_response = make_api_request(
                base_url=self.client.base_url,
                endpoint=f"{self.endpoint}/{harness_config_id}/stages",
                method="post",
                data=staging_payload,
                token=self.client.api_key
            )
            staging_id = staging_response.get("id")
        except Exception as e:
            raise ValueError(f"Failed to initialize harness staging: {e}")
        
        # step 2 and step 2.5: only if policy files are there
        if "AGENT_POLICY" in category and policy_file_path:
            # step 2: get a signed URL with file info
            file_size = os.path.getsize(policy_file_path) # type: ignore
            checksum = calculate_md5_base64(policy_file_path) # type: ignore
            #file must be .pdf or  .txt
            if policy_file_path.endswith(".pdf"):
                file_type = "application/pdf"
            elif policy_file_path.endswith(".txt"):
                file_type = "text/plain"
            else:
                raise ValueError("Policy file must be a .pdf or .txt file.")
            
            signed_url_payload = {
                "category": "AGENT_POLICY",
                "file_name": policy_file_path, # just take raw filename
                "file_size": file_size,
                "file_type": file_type,
                "checksum": checksum
            }
            try:
                signed_url_response = make_api_request(
                    base_url=self.client.base_url,
                    endpoint=f"{self.endpoint}/{harness_config_id}/stages/{staging_id}/files",
                    method="post",
                    data=signed_url_payload,
                    token=self.client.api_key
                )
            except Exception as e:
                raise ValueError(f"Failed to create signed URL for policy upload: {e}")
            
            # step 3: upload file using signed URL
            with open(policy_file_path, 'rb') as f: # type: ignore
                policy_content = f.read()
            try:
                file_upload_response = requests.put(
                    signed_url_response["upload_url"],
                    data=policy_content,
                    headers={
                        'Content-Type': file_type,
                        'Content-MD5': checksum
                    }
                )
            except Exception as e:
                raise ValueError(f"Failed to upload policy file: {e}")
            if file_upload_response.status_code != 200:
                raise ValueError(f"Failed to upload policy file: {file_upload_response.text}")            
        
            #step 3: verify file upload
            try:
               make_api_request(
                    base_url=self.client.base_url,
                    endpoint=f"{self.endpoint}/{harness_config_id}/stages/{staging_id}/files",
                    method="get",
                    params={'staging_id': staging_id},
                    token=self.client.api_key
                )
            except Exception as e:
                raise ValueError(f"Policy file not uploaded: {e}")

        # step 4: staging complete api call
        function_route_params = {
                "input_schema": str(input_schema),
                "output_schema": str(output_schema),
                "function_route": function_route
            } if "FUNCTION_ROUTE" in category else None
        rag_params = {"bucket_name": kb_bucket} if "KNOWLEDGE_BASE" in category else None
        try:
            staging_complete_response = make_api_request(
                base_url=self.client.base_url,
                endpoint=f"{self.endpoint}/{harness_config_id}/stages/{staging_id}/complete",
                method="put",
                data={
                    "harness_types": category,
                    "function_route_params": function_route_params,
                    "rag_params": rag_params
                },
                token=self.client.api_key
            )
        except Exception as e:
            raise ValueError(f"Failed to create harness: {e}")
        
        return {
            "harness_name": name,
            "harness_config_id": harness_config_id,
            "status": staging_complete_response.get("status"),
        }
        
    def get_status(self, harness_id: str):
        """
        Get the status of a harness.
        
        :param harness_id: The ID of the harness.
        :return: The status of the harness.
        :rtype: str
        """
        all_status = make_api_request(
            base_url=self.client.base_url,
            endpoint="harness-config-stages",
            token=self.client.api_key
        ).get("results")
        for status in all_status:
            if status.get("harness_config_id") == harness_id:
                return status
            
        return f"Harness {harness_id} not found. Please check the ID and try again."

    def delete(self, harness_id: str):
        """
        Not implemented yet.
        """
        raise NotImplementedError("Delete harnesses is not implemented yet.")
        
        #if request is succeessful, return the harness id, name, and a "submitted" message
        return make_api_request(
            base_url=self.client.base_url,
            endpoint=f"harness-configs/{harness_id}",
            method="delete",
            token=self.client.api_key
        )
    
class Evaluations:
    """Class for handling evaluations API requests.
    
    :param client: The VijilClient instance.
    :type client: VijilClient
    """
    
    def __init__(
        self,
        client: VijilClient
    ) -> None:
        self.endpoint = "evaluations"
        self.client = client
        self.api_proxy_dict: dict = field(default_factory=dict)
        self.detectors = Detectors(client)
    
    def list(self, limit=10):
        """List all valuations. Will return only 10 evaluations unless specified.
        
        :param limit: The number of evaluations to return, defaults to 10.
        :type limit: int, optional
        """

        response = make_api_request(
            base_url=self.client.base_url, 
            endpoint=self.endpoint+"?limit="+str(limit), 
            token=self.client.api_key
        )
        return response['results']
    
    def create(self, model_hub: str, harness_version: Optional[str]="1.2.27", model_name: Optional[str]=None, name: Optional[str]=None, api_key_name: Optional[str]=None, model_url: Optional[str]=None, model_params={}, harness_params={}, harnesses=[]):
        """Create a new evaluation.

        :param model_hub: The model hub you want to use. Supported options are "openai", "together", "digitalocean", "custom".
        :type model_hub: str
        :param harness_version: The version of the harness you want to use.
        :type harness_version: str
        :param model_name: The name of the model you want to use. Check the model hub's API documentation to find valid names.
        :type model_name: str, optional
        :param name: The name of the evaluation. If not specified, model hub will be concatenated with model name.
        :type name: str, optional
        :param api_key_name: The name of the model hub API key you want to use. If not specified, will use the first key we find for the specified model_hub.
        :type api_key_name: str, optional
        :param model_url: The URL of the model you want to use. Only required for custom model hub. Defaults to None
        :type model_url: str, optional
        :param model_params: A dictionary specifying inference parameters like temperature and top_p. If none are specified, model hub defaults will be used. Defaults to {}
        :type model_params: dict, optional
        :param harness_params: Set optional parameters like is_lite, defaults to {}
        :type harness_params: dict, optional
        :param harnesses: A list of harnesses you want to include in the evaluation, defaults to []
        :type harnesses: List[str], optional
        :raises TypeError: If you have no API keys stored.
        :raises ValueError: If you have no API keys stored for the specified model hub.
        :raises ValueError: If you supply an api_key_name that does not exist.
        :raises ValueError: If you specify lite mode for any harness other than ethics.
        :return: API response containing evaluation ID of the newly created evaluation.
        :rtype: dict
        """

        model_hub = modify_hub(model_hub)

        # store all api keys in a dictionary if not there
        if self.api_proxy_dict.__class__.__name__=="Field":
            try:
                self.api_proxy_dict = get_api_proxy_dict(base_url=self.client.base_url, token=self.client.api_key)
            except TypeError:
                raise TypeError("No API keys found. Please upload an API key first.")
            
        # get api key proxy for the model hub
        try:
            hub_api_proxy_dict = self.api_proxy_dict[model_hub]
        except KeyError: 
            raise ValueError(f"No API key stored for model hub {model_hub}")
        
        # get api key proxy for the model hub
        if api_key_name is not None:
            #find api key id for the api key name
            if api_key_name not in hub_api_proxy_dict.keys():
                raise ValueError(f"No API key found for name {api_key_name}")
            else:
                api_key_proxy = hub_api_proxy_dict[api_key_name]
        else: #if no key specified, use first value in hub dictionary
            api_key_proxy = next(iter(hub_api_proxy_dict.values()))

        # create the payload
        payload = {
            # "name": name if name else f"{SUPPORTED_HUBS[model_hub]}-{model_name}",
            "name": name if name else f"{SUPPORTED_HUBS[model_hub]}-{model_name}-{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}",       
            "id": str(uuid.uuid4()),
            "hub": model_hub,
            "api_key_proxy": api_key_proxy,
            "scenario_config_filters": [],
            "agent_params": {"temperature": 0, "top_p": 1, "max_tokens": 125},
            "is_lite": False,
            "tags": [""],
            "version": harness_version
        }
        if model_hub in HUBS_NOT_NEEDING_MODEL_NAME:
            payload["model"] = "n/a"
        else:
            try:
                payload["model"] = model_name
            except KeyError:
                raise ValueError(f"No model name specified for {model_hub}. Please specify a model name.")
            
        if model_hub in HUBS_NEEDING_URL:
            if model_url is None:
                raise ValueError("For this model hub, you must specify a model URL.")
            if model_hub=="custom" and api_key_name is None:
                raise ValueError("For custom model hubs, you must specify an API key name. Use `api_keys.list()` to see available keys.")
            payload["url"] = model_url
        
        if model_params:
            for key, value in model_params.items():
                payload["agent_params"][key] = value
            if model_params.get("num_generations"):
                payload["num_generations"] = model_params["num_generations"]
        for option in ["sample_size", "is_lite"]:
            if harness_params.get(option):
                payload[option] = harness_params[option]
        
        if "trust_score" in harnesses:
            if len(harnesses)==1:
                harnesses_modified = ["security","privacy","hallucination","robustness","toxicity","stereotype","fairness","ethics","OpenLLM"]
            else:
                raise ValueError("The `trust_score` harness is available only as a standalone harness.")
        else:
            harnesses_modified = harnesses
        payload["harness_config_ids"] = [f"vijil.harnesses.{h}" for h in harnesses_modified]        

        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint,
            method="post",
            data=payload,
            token=self.client.api_key
        )
        
    def get_status(self, evaluation_id: str):
        """Retrieve the status of an evaluation

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :return: A dict with the id, status, and other metadata of the evaluation
        :rtype: dict
        """

        response = make_api_request(base_url=self.client.base_url, endpoint=f"evaluations/{evaluation_id}", token=self.client.api_key)
        return response

    def get_tree(self, evaluation_id: str):
        """
        Retrieve the tree of an evaluation

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :return: For each probe, information about which harness and scenario it came from
        :rtype: dict
        """

        # harness level
        try:
            harness_info = make_api_request(base_url=self.client.base_url, endpoint=f"harness?evaluation_id={evaluation_id}", token=self.client.api_key)
        except Exception as e:
            raise ValueError(f"Error getting harness info: {e}")

        # scenario level
        try:
            scenario_info = make_api_request(base_url=self.client.base_url, endpoint=f"scenarios?evaluation_id={evaluation_id}", token=self.client.api_key)
        except Exception as e:
            raise ValueError(f"Error getting scenario info: {e}")

        # probe level
        try:
            probe_info = make_api_request(base_url=self.client.base_url, endpoint=f"probes?evaluation_id={evaluation_id}", token=self.client.api_key)
        except Exception as e:
            raise ValueError(f"Error getting probe info: {e}")

        # build tree
        tree = {}
        for harness in harness_info['results']:
            tree[harness['config_id']] = {
                'name': harness['name'],
                'type': 'harness',
                'children': harness['scenario_config_ids']
            }
        for scenario in scenario_info['results']:
            tree[scenario['config_id']] = {
                'name': scenario['name'],
                'type': 'scenario',
                'children': scenario['probe_config_ids']
            }
        for probe in probe_info['results']:
            tree[probe['config_id']] = {
                'name': probe['name'],
                'type': 'probe',
                'children': probe['prompt_ids']
            }
        return tree

    def get_ancestry(self, tree: dict, node_id: str):
        """
        Retrieve the ancestry of a node in the tree

        :param tree: The tree of the evaluation
        :type tree: dict
        :param node_id: The unique ID of the node
        :type node_id: str
        :return: a dict with each ancestor as a value and ancestor types as the keys
        :rtype: dict
        """

        ancestors = {}
        node_value = tree.get(node_id) #value of node
        if node_value is None:
            raise ValueError(f"Node {node_id} not found in tree.")
        current_node = node_value
        current_node_id = node_id
        while current_node['type'] != 'harness':
            for parent_id, parent in tree.items():
                if current_node_id in parent['children']:
                    ancestors[parent['type']] = {"id": parent_id, "name": parent['name']}
                    current_node = parent
                    current_node_id = parent_id
                    break
        return ancestors


    def summarize(self, evaluation_id: str):
        """
        Return summary dataframe of the evaluation results, aggregated at every level
        (overall eval, dimension, scenario, probe)

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :return: A dataframe with the level, level_name, and score of the evaluation
        :rtype: pandas.DataFrame
        """

        #initalize list of dicts where keys are level, level_name, score
        summary_rows = []
        
        # get status of evaluation
        try:
            status_dict = self.get_status(evaluation_id=evaluation_id)
        except ValueError as e: # for when evaluation doesn't exist
            raise e
        
        # evaluation level
        if status_dict['status']=='COMPLETED':
            row = dict()
            row['level'] = 'overall'
            row['level_name'] = 'evaluation'
            row['score'] = round(status_dict['score']*100, 2)
            summary_rows.append(row)            
        else:
            raise ValueError("Evaluation is not completed yet, check back later.")
        
        # harness level
        response = make_api_request(base_url=self.client.base_url, endpoint=f"harness?evaluation_id={evaluation_id}", token=self.client.api_key)
        for harness in response['results']:
            if harness['harness_type']=='DIMENSION' and harness['score'] is not None:
                row = dict()
                row['level'] = 'harness'
                row['level_name'] = harness['name']
                row['score'] = round(harness['score']*100, 2)
                summary_rows.append(row)   
                
        # scenario level
        response = make_api_request(base_url=self.client.base_url, endpoint=f"scenarios?evaluation_id={evaluation_id}", token=self.client.api_key)
        for scenario in response['results']:
            if scenario['score'] is not None:
                row = dict()
                row['level'] = 'scenario'
                row['level_name'] = scenario['name']
                row['score'] = round(scenario['score']*100, 2)
                summary_rows.append(row)
                
        # probe level
        response = make_api_request(base_url=self.client.base_url, endpoint=f"probes?evaluation_id={evaluation_id}", token=self.client.api_key)
        for probe in response['results']:           
            if probe['score'] is not None:
                row = dict()
                row['level'] = 'probe'
                row['level_name'] = probe['name']
                row['score'] = round(probe['score']*100, 2)
                summary_rows.append(row)
                
        return pd.DataFrame(summary_rows)
        
    def export_summary(self, evaluation_id: str, output_dir: str = './', format: str='pdf'):
        """
        Export a PDF or HTML report of the evaluation results containing evaluation metadata
        plus stats from summarize() function

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :param output_dir: The directory to save the report to. Defaults to current directory
        :type output_dir: str
        :param format: The format of the report. Defaults to pdf. Options are 'pdf' and 'html'
        :type format: str
        :raises ValueError: If specified format is not 'pdf' or 'html'
        """
        #get dataframe of summary stats
        summary = self.summarize(evaluation_id=evaluation_id)

        #get evaluation metadata
        status_dict = self.get_status(evaluation_id=evaluation_id)

        #set jinja settings
        HOME = os.path.join(os.path.dirname(__file__), ".")
        templateLoader = jinja2.FileSystemLoader(
            searchpath=HOME + "/templates"
        )
        templateEnv = jinja2.Environment(loader=templateLoader)
        header_template = templateEnv.get_template("vijil_header.jinja")
        footer_template = templateEnv.get_template("vijil_footer.jinja")
        pdf_template = templateEnv.get_template("whole_pdf.jinja")

        filename = evaluation_id + '_summary.' + format

        data_fields = {
            "reportfile": filename,
            "run_uuid": evaluation_id,
            "start_time": str(datetime.fromtimestamp(status_dict['created_at'], tz=timezone.utc)) + " UTC",
            "created_by": status_dict['created_by'],
            "end_time": str(datetime.fromtimestamp(status_dict['completed_at'], tz=timezone.utc)) + " UTC",
            "model_name": status_dict["model"],
            'total_test_count': status_dict['total_test_count'],
            'completed_test_count': status_dict['completed_test_count'],
            'error_test_count': status_dict['error_test_count'],
            "results": summary.to_html(index=False)
        }

        #write to file
        if format=='html': #use header and footer templates for html

            # render the header.
            digest_content = header_template.render(data_fields)            
            # render the footer
            digest_content += footer_template.render()

            with open(os.path.join(output_dir, filename), "w") as f:
                f.write(digest_content)

        elif format=='pdf': #use whole_pdf template which leaves out CSS and JS
            digest_content = pdf_template.render(data_fields)            
            pdf = FPDF()
            pdf.add_page()
            pdf.write_html(digest_content)
            pdf.output(os.path.join(output_dir, filename))
        else:
            raise ValueError("format must be 'html' or 'pdf'") 
    
    def describe(self, evaluation_id: str, limit: int = 1000, format: str = "dataframe", prettify: bool = True, hits_only: bool=False):
        """
        Return either list or dataframe of prompt-level metadata and evaluation results,
        with metadata and evaluation scores for each prompt/response in the given evaluation id.

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :param limit: The maximum number of prompts to include in description. Defaults to 1000.
        :type limit: int, optional
        :param format: The format of the output. Defaults to "dataframe". Options are "dataframe" and "list"
        :type format: str, optional
        :raises ValueError: If specified format is not 'dataframe' or 'list'
        :param prettify: If True, will remove the "vijil.probes." prefix from the probe names to make it more readable. Defaults to True.
        :type prettify: bool, optional
        :type hits_only: bool, optional
        :param hits_only: If True, will only return prompts that had undesirable responses (according to our detectors). Defaults to False.
        """
        if limit is None:
            limit = 1000000
        
        response = make_api_request(
            base_url=self.client.base_url, 
            endpoint=f"responses?evaluation_id={evaluation_id}&limit={limit}&is_visible=true", 
            token=self.client.api_key
        )

        # change detector ids to list if it is a string
        results = response['results']
        if len(results) == 0:
            raise ValueError(f"No results found for evaluation id {evaluation_id}. Please check that you have the correct id.")
        for idx, res in enumerate(results):
            if isinstance(res['detector_ids'], str): #modify this to accomodate >1 detector_id
                #split by comma and remove whitespace
                results[idx]['detector_ids'] = [d.strip() for d in res['detector_ids'].split(',')]

        prompt_list = [
            {
                "probe": res['probe_config_id'],
                "input_prompt_id": res['input_prompt_id'],
                "prompt": res['input_prompt'],
                "prompt_list": res['prompt'],
                'prompt_group': res['prompt_group'],
                "response": res['response'],
                "detectors": res['detector_ids'],
                "detector_scores": res['detector_scores'],
                "score": res.get('score', {}).get('score') if res.get('score') is not None else None,
                "triggers": res.get('triggers', []),
                'generation': res['generation'],
                'status': res['status'],
                'error_message': res['error_message']
            }
            for res in results
        ]

        #convert to df for easier data processing
        prompt_list_df = pd.DataFrame(prompt_list)

        #get probe metadata
        probes = self.get_probes_info(evaluation_id=evaluation_id)
        #above returns a list of dicts with keys: probe, name, description, scoring_function
        #populate probe column in prompt_list_df with name from probes dict
        prompt_list_df['probe_name'] = prompt_list_df['probe'].apply(lambda x: [p['name'] for p in probes if p['probe'] == x][0])
        prompt_list_df['probe_description'] = prompt_list_df['probe'].apply(lambda x: [p['description'] for p in probes if p['probe'] == x][0])
        prompt_list_df['probe_scoring_function'] = prompt_list_df['probe'].apply(lambda x: [p['scoring_function'] for p in probes if p['probe'] == x][0])

        #get detector metadata
        detectors = prompt_list_df['detectors'].values 
        flattened_detectors = [item for sublist in detectors for item in sublist]
        unique_detectors = set(flattened_detectors)
        detector_metadata = {det: self.detectors.get_detector_info(detector_id=det) for det in unique_detectors}
        prompt_list_df['detector_names'] = prompt_list_df['detectors'].apply(lambda dets: [detector_metadata[det]['name'] for det in dets])
        prompt_list_df['detector_descriptions'] = prompt_list_df['detectors'].apply(lambda dets: [detector_metadata[det]['description'] for det in dets])

        #get harness and scenario each response belongs to
        tree = self.get_tree(evaluation_id=evaluation_id)
        #column function on 'probe' column. Get ancestors of each probe. Assign to new columns harness, harness_name, scenario, scenario_name
        prompt_list_df['harness'] = prompt_list_df['probe'].apply(lambda x: self.get_ancestry(tree, x)['harness']['id'])
        prompt_list_df['harness_name'] = prompt_list_df['probe'].apply(lambda x: self.get_ancestry(tree, x)['harness']['name'])
        prompt_list_df['scenario'] = prompt_list_df['probe'].apply(lambda x: self.get_ancestry(tree, x)['scenario']['id'])
        prompt_list_df['scenario_name'] = prompt_list_df['probe'].apply(lambda x: self.get_ancestry(tree, x)['scenario']['name'])

        #joins for displaying second prompt in pairwise prompts
        prompt_list_df['prompt_group_len'] = prompt_list_df['prompt_group'].apply(lambda x:  len(x))
        pairwise = prompt_list_df[prompt_list_df['prompt_group_len'] == 2]
        nonpairwise = prompt_list_df[prompt_list_df['prompt_group_len'] != 2]
        pairwise['input_prompt_id2'] = pairwise['prompt_group'].apply(lambda x: x[1])
        pairwise_with_prompt2_text = pairwise.merge(pairwise[['input_prompt_id', 'prompt', 'response']].rename(columns={'input_prompt_id': 'input_prompt_id2', 'prompt': 'prompt2', 'response': 'response2'}), on='input_prompt_id2', how='inner')
        #filter out rows with skipped responses---these do not add any information since their reversed counterparts will be included
        pairwise_with_prompt2_text = pairwise_with_prompt2_text[pairwise_with_prompt2_text['detector_scores'].apply(lambda x: not any(['SKIP' in item for item in x]))]
        #add empty columns to nonpairwise rows
        nonpairwise['input_prompt_id2'] = None
        nonpairwise['prompt2'] = None
        nonpairwise['response2'] = None
        #concatenate pairwise and nonpairwise dfs row-wise
        output_df = pd.concat([pairwise_with_prompt2_text, nonpairwise], axis=0)
        #drop prompt_group_len column which we needed only for processing
        output_df.drop(columns=['prompt_group_len'], inplace=True)

        if hits_only:
            output_df = output_df[output_df['score']==0]

        #prettify probe names
        if prettify:
            output_df['probe'] = output_df['probe'].apply(lambda x: x.replace("vijil.probes.", ""))

        #sort by probes for easier viewing
        output_df.sort_values('probe', inplace=True)

        if format=='list':
            return output_df.to_dict(orient='records')
        elif format=='dataframe':
            return output_df
        else:
            raise ValueError("format must be 'list' or 'dataframe'")

    
    def export_report(self, evaluation_id: str, limit: int=1000000, format: str='csv', output_dir: str = './', prettify: bool = True, hits_only: bool=False):
        """
        Exports output of describe() into csv, jsonl, json, or parquet 

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :param limit: The maximum number of prompts to include in the report. Defaults to 1000000.
        :type limit: int, optional
        :param format: The format of the output. Defaults to "csv". Options are "csv", "parquet", "json" and "jsonl"
        :type format: str, optional
        :raises ValueError: If specified format is not 'csv', 'parquet', 'json' or 'jsonl'
        :param output_dir: The directory to save the report. Defaults to the current directory.
        :type output_dir: str, optional
        :param prettify: If True, will remove the "vijil.probes." prefix from the probe names to make it more readable. Defaults to True.
        :type prettify: bool, optional
        :type hits_only: bool, optional
        :param hits_only: If True, will only return prompts that had undesirable responses (according to our detectors). Defaults to False.        
        """

        if format=='csv':
            prompt_list_df = self.describe(evaluation_id=evaluation_id, limit=limit, format="dataframe", prettify=prettify, hits_only=hits_only)
            filename = evaluation_id + '_report.csv'
            filepath = os.path.join(output_dir, filename)            
            prompt_list_df.to_csv(filepath, index=False)
            print("report exported to " + filepath)
        elif format=='json':
            prompt_list = self.describe(evaluation_id=evaluation_id, limit=limit, format="list", prettify=prettify, hits_only=hits_only)
            filename = evaluation_id + '_report.json'
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(prompt_list, f, indent=4)
            print("report exported to " + filepath)
        elif format=='jsonl':
            prompt_list = self.describe(evaluation_id=evaluation_id, limit=limit, format="list", prettify=prettify, hits_only=hits_only)
            filename = evaluation_id + '_report.jsonl'
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                for item in prompt_list:
                    f.write(json.dumps(item) + '\n')
            print("report exported to " + filepath)
        elif format=='parquet':
            prompt_list_df = self.describe(evaluation_id=evaluation_id, limit=limit, format="dataframe", prettify=prettify, hits_only=hits_only)
            filename = evaluation_id + '_report.parquet'
            filepath = os.path.join(output_dir, filename)
            prompt_list_df.to_parquet(filepath, index=False)
            print("report exported to " + filepath)
        else:
            raise ValueError("format must be 'csv', 'parquet', 'json', or 'jsonl'")

    def cancel(self, evaluation_id: str):
        """
        Cancels an in-progress evaluation

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :raises ValueError: If the evaluation is not in progress
        :returns: The response from the API
        :rtype: dict
        """

        #check eval status
        try:
            status_dict = self.get_status(evaluation_id=evaluation_id)
        except ValueError as e:
            return e
        
        if status_dict['status'] != 'IN_PROGRESS':
            raise ValueError(f"Evaluation {evaluation_id} is not in progress. Cannot cancel.")
        
        payload = {
                    "type": "CANCEL_EVALUATION",
                    "data": {
                        "evaluation_id": evaluation_id
                    }
                  }
        
        return make_api_request(
            base_url=self.client.base_url,
            endpoint="events",
            method="post",
            data=payload,
            token=self.client.api_key
        )
    
    def delete(self, evaluation_id: str):
        """
        Deletes an evaluation

        :param evaluation_id: The unique ID of the evaluation
        :type evaluation_id: str
        :raises ValueError: If the evaluation does not exist
        :returns: The response from the API
        :rtype: dict
        """

        #check eval status. This will raise an error if the eval doesn't exist.
        try:
            self.get_status(evaluation_id=evaluation_id)
        except ValueError as e:
            return e
        
        payload = {
                    "type": "DELETE_EVALUATION",
                    "data": {
                        "evaluation_id": evaluation_id
                    }
                  }
        
        return make_api_request(
            base_url=self.client.base_url,
            endpoint="events",
            method="post",
            data=payload,
            token=self.client.api_key
        )

    def get_probes(self, evaluation_id: str):
        """
        Get all probes and probe metadata for a specific evaluation.
        Returns a dict with keys results, count.
        Results array contains probes and count indicates number of probes.
        """
        try:
            response = make_api_request(
                base_url=self.client.base_url,
                endpoint="probes",
                token=self.client.api_key,
                params={"evaluation_id": evaluation_id}
            )
        except Exception as e:
            raise ValueError(f"Error getting probes for evaluation {evaluation_id}: {e}")

        #return only probe info
        return response["results"]

    def get_probes_info(self, evaluation_id: str):
        """
        Get metadata for all probes in a specific evaluation.
        Returns a list of dicts with keys: probe, name, description, scoring_function.
        """
        probes = self.get_probes(evaluation_id=evaluation_id)
        #return the following metadata: config_id, name, description, scoring_function
        return [{"probe": p["config_id"], "name": p["name"], "description": p["description"], "scoring_function": p["scoring_function"]} for p in probes]


class Detectors:
    """Class for handling API requests to get detector metadata."""

    def __init__(self, client: VijilClient) -> None:
        self.endpoint = "detectors"
        self.client = client

    def get_detector_info(self, detector_id: str, version: str=OBJECTS_VERSION): 
        """Gets all detector metadata"""
        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint + f"/{detector_id}",
            token=self.client.api_key,
            params={"version": version}
        )

    def list(self, version: str=OBJECTS_VERSION):
        """Lists all available detectors"""
        return make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint,
            token=self.client.api_key,
            params={"version": version}
        )

class Detections:
    """Class for handling detections API requests.
    :param detector_id: The unique ID of the detector
    :type detector_id: str
    :param detector_inputs: Input payload to the detector
    :type detector_inputs: List[dict]
    :param detector_params: Optional parameters to be passed for the detector
    :type detector_params: dict
    """
    
    def __init__(self, client: VijilClient) -> None:
        """Initialize the Detections class.

        :param client: The Vijil client instance.
        :type client: VijilClient
        """
        self.endpoint = "detections"
        self.client = client
        self.api_proxy_dict: dict = field(default_factory=dict)
        self.detector_list = []
        for k, v in DETECTOR_LIST.items():
            self.detector_list += v
        
    def list_detectors(self):
        return self.detector_list
        
    def create(self, detector_id: str, detector_inputs: List[dict], detector_params: Optional[dict] = None):
        """Create a new detection.

        :param detector_id: The unique ID of the detector
        :type detector_id: str
        :param detector_inputs: Input payload to the detector
        :type detector_inputs: List[dict]
        :param detector_params: Optional parameters to be passed for the detector
        :type detector_params: dict
        :return: The response from the API
        :rtype: dict
        """
        
        # make full detector id
        full_detector_id = None
        for k, v in DETECTOR_LIST.items():
            for detname in v:
                if detname==detector_id:
                    full_detector_id = f"{k}.detectors.{detname}"
                    break
        if not full_detector_id:
            raise ValueError(f"Detector {detector_id} not found. use `detectors.list_detectors()` to see available detectors.")
        
        payload = {
            "id": str(uuid.uuid4()),
            "detector_id": full_detector_id,
            "detector_inputs": detector_inputs,
        }
                
        # add detector params if necessary
        if full_detector_id in DEFAULT_DETECTOR_PARAMS.keys():
            if detector_params is None:
                detector_params = DEFAULT_DETECTOR_PARAMS[full_detector_id] 
                
            # add api key proxy TODO: refactor later, double code with evaluations.create

            # store all api keys in a dictionary if not there
            if self.api_proxy_dict.__class__.__name__=="Field":
                try:
                    self.api_proxy_dict = get_api_proxy_dict(base_url=self.client.base_url, token=self.client.api_key)
                except TypeError:
                    raise TypeError("No API keys found. Please upload an API key first.")
                
            # get api key proxy dict for the model hub
            hub = modify_hub(detector_params["hub"])
            try:
                hub_api_proxy_dict = self.api_proxy_dict[hub]
            except KeyError: 
                raise ValueError(f"No API key stored for model hub {hub}")
            
            # get api key proxy for the model hub
            if detector_params.get("api_key_name"):
                api_key_name = detector_params["api_key_name"]
                #find api key id for the api key name
                if api_key_name not in hub_api_proxy_dict.keys():
                    raise ValueError(f"No API key found for name {api_key_name}")
                else:
                    api_key_proxy = hub_api_proxy_dict[api_key_name]
            else: #if no key specified, use first value in hub dictionary
                api_key_proxy = next(iter(hub_api_proxy_dict.values()))
                
            detector_params = {
                "api_key_proxy": api_key_proxy,
                "hub": hub,
                "model": detector_params["model"]
            }
        else:
            detector_params = {"api_key_proxy": "", "hub": "", "model": ""}
        payload["detector_params"] = detector_params # type: ignore
        
        msg = make_api_request(
            base_url=self.client.base_url,
            endpoint=self.endpoint,
            method="post",
            data=payload,
            token=self.client.api_key
        )
        return {"id": msg["id"], "status": msg["status"]}
        
    def get_status(self, detection_id: str):
        """Retrieve the status of a detection.

        :param detection_id: The unique ID of the detection
        :type detection_id: str
        :return: The response from the API
        :rtype: dict
        """
        
        raw_output = make_api_request(
            base_url=self.client.base_url,
            endpoint=f"detections/{detection_id}",
            token=self.client.api_key
        )
        return {"id": raw_output["id"], "status": raw_output["status"]}
    
    def describe(self, detection_id: str, format: str = "dataframe"):
        """Describe a detection.

        :param detection_id: The unique ID of the detection
        :type detection_id: str
        :return: The response from the API
        :rtype: dict
        """
        input_fields = ["response","triggers","ground_truth","question","contexts","instructions","kwargs","forbidden_prompt","role","expected_tools","input","policy"]
        output_fields = ["score","reason","error"]
        
        raw_output = make_api_request(
            base_url=self.client.base_url,
            endpoint=f"detections/{detection_id}",
            token=self.client.api_key
        )
        if raw_output["status"] != "COMPLETED":
            raise ValueError(f"Detection {detection_id} is not completed yet. Please check back later.")
        else:
            raw_detector_inputs = raw_output["detector_inputs"]
            raw_detector_outputs = raw_output["detector_outputs"]
            
            # process inputs
            detector_inputs = []
            for input_dict in raw_detector_inputs:
                detector_inputs.append({
                    "input_id": input_dict["id"],
                    "detector_input": {k: input_dict[k] for k in input_dict if k in input_fields},
                    "status": raw_output["status"]
                })
                
            # process outputs
            detector_outputs = []
            for output_dict in raw_detector_outputs:
                detector_outputs.append({
                    "input_id": output_dict["input_id"],
                    "detector_output": {k: output_dict[k] for k in output_dict if k in output_fields},
                })
                
            # merge and reorder
            output_df = pd.DataFrame(detector_inputs).merge(pd.DataFrame(detector_outputs), on="input_id")
            output_df['detector_id'] = raw_output["detector_id"]
            output_df = output_df[['detector_id', 'status', 'detector_input', 'detector_output']]
            
            # return
            if format=='list':
                return output_df.to_dict(orient='records')
            elif format=='dataframe':
                return output_df
            else:
                raise ValueError("format must be 'list' or 'dataframe'")

class Vijil:
    """Base class for the Vijil API client.
    
    :param base_url: The base URL for the Vijil API
    :type base_url: str
    :param api_key: The API key for the Vijil API
    :type api_key: str
    """
    client: VijilClient
    evaluations: Evaluations
    harnesses: Harnesses
    detections: Detections
    api_keys: APIKeys
    
    def __init__(self, base_url: str = BASE_URL, api_key: Optional[str] = None):
        """Constructor class for VijilClient

        :param base_url: Base URL for API, defaults to BASE_URL as specified in `api.py`
        :type base_url: str, optional
        :param api_key: Vijil API key, defaults to None
        :type api_key: str, optional
        :raises ValueError: if no Vijil API key is provided in api_key and VIJIL_API_KEY is not set as an environment variable
        """
                
        if api_key is None:
            api_key = os.environ["VIJIL_API_KEY"]
        if api_key is None:
            raise ValueError(
                "No API key found! Please set VIJIL_API_KEY as environment variable or supply the `api_key` parameter."
            )
            
        self.client = VijilClient(base_url=base_url, api_key=api_key)
        self.evaluations = Evaluations(self.client)
        self.harnesses = Harnesses(self.client)
        self.detections = Detections(self.client)
        self.api_keys = APIKeys(self.client)
        self.detectors = Detectors(self.client)
