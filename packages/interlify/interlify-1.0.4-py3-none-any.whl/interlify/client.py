import requests
import json
import logging
from urllib.parse import quote
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Interlify:
    def __init__(
        self,
        api_key: str,
        project_id: str,
        base_url: str = "https://www.interlify.com",
        auth_headers: List[Dict[str, str]] = None
    ):
        """
        Initializes the client with API key, project ID, and optional configurations.
        
        :param api_key: Your Interlify API key
        :param project_id: Your project ID
        :param base_url: Base API URL (default: production)
        :param auth_headers: Additional authentication headers as a dictionary
        """
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url.rstrip('/')
        self.auth_headers = auth_headers or []
        self.project_tools: List[Dict[str, Any]] = []
        self._initialized = False

    def _initialize(self) -> None:
        """Fetch project tools from server. Raises exceptions on failure."""
        if self._initialized:
            return

        endpoint = f"{self.base_url}/api/projects/{self.project_id}"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

        try:
            response = requests.post(endpoint, headers=headers)
            response.raise_for_status()
            self.project_tools = json.loads(response.json())
      
            self._initialized = True
            
        except requests.exceptions.RequestException as e:
            logger.error("Initialization failed: %s", str(e))
            raise RuntimeError(f"Initialization failed: {str(e)}") from e

    def get_tools(self) -> List[Dict[str, Any]]:
        """Returns list of available tools with their metadata."""
        self._initialize()

        tools_list = []
        for tool in self.project_tools:
            tool_name = tool.get("function", {}).get("name")
            function_config = tool.get("function")
            
            # Create a new method for each tool to support openai agent sdk
            # OpenAI Agent SDK requires passing a ctx into the tool funciton: https://openai.github.io/openai-agents-python/tools/
            # It must be async for OpenAI agent
            async def tool_function(ctx:any, arguments: Dict[str, Any], tool_name = tool_name) -> Dict[str, Any]:
                result = self.call_tool(tool_name, arguments)
                return json.dumps(result)
            
            # Set the function name for better identification
            tool_function.__name__ = tool_name
            
            tools_list.append({
                "name": tool_name,
                "type": tool.get("type"),
                "description": tool.get("function", {}).get("description"),
                "function": function_config,
                "tool_function": tool_function  # Assign the newly created function
            })

    def _call_api(
        self,
        function_config: Dict[str, Any],
        func_arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Internal method to execute API requests with proper error handling."""
        try:
            # Build URL
            endpoint = function_config["url"]

            # Substitute path parameters
            path_params = function_config.get("pathParams", [])
            for param in path_params:
                if param not in func_arguments:
                    raise ValueError(f"Missing required path parameter: {param}")
                endpoint = endpoint.replace(
                    f"{{{param}}}", 
                    quote(str(func_arguments[param])))
                
            # Handle query parameters
            query_params = function_config.get("queryParams", [])
            query = {
                param: func_arguments[param]
                for param in query_params
                if param in func_arguments
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            # Merge auth_headers (list of dicts) into headers
            for auth_header in self.auth_headers:
                headers.update(auth_header)
            
            # Prepare request components
            method = function_config.get("method", "GET").upper()
            body = None
            
            if method in ("POST", "PUT", "PATCH"):
                body_params = function_config.get("body", [])
                body_data = {
                    param: func_arguments[param]
                    for param in body_params
                    if param in func_arguments
                }
                body = json.dumps(body_data)

            # Execute request
            response = requests.request(
                method=method,
                url=endpoint,
                params=query,
                headers=headers,
                data=body,
                timeout=10
            )
            response.raise_for_status()

            return {
                "status": response.status_code,
                "data": response.json() if response.content else None
            }

        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s", str(e))
            raise RuntimeError(f"API request failed: {str(e)}") from e

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes a tool with provided arguments.
        
        :param tool_name: Name of the tool to execute
        :param arguments: Dictionary of arguments for the tool
        :return: API response data
        """
        self._initialize()

        # Handle when arugements are passed as string by LLMs
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        
        # Find the requested tool
        tool = next(
            (t for t in self.project_tools 
             if t.get("function", {}).get("name") == tool_name),
            None
        )
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        function_config = tool.get("functionConfig")
        if not function_config:
            raise RuntimeError(f"Missing configuration for tool '{tool_name}'")
            
        return self._call_api(function_config, arguments)