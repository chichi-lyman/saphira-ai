import inspect
import json
import asyncio
from typing import Callable, Dict, Any, List, Optional, Union

class PluginRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register_tool(self, name: str, description: str, schema: Optional[Dict[str, Any]] = None):
        """
        Decorator to register custom tools dynamically.
        If no schema is provided, standard JSON Schema types are inferred from docstrings and hints.
        """
        def decorator(func: Callable):
            self._tools[name] = func
            
            tool_schema = schema or self._generate_schema_from_func(func, description)
            self._schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": tool_schema
                }
            })
            return func
        return decorator

    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Executes a tool asynchronously, handling both sync and async functions seamlessly."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' is not registered in Saphira's Plugin Registry.")
        
        func = self._tools[tool_name]
        
        if asyncio.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            # Run sync functions in an executor to keep the event loop non-blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(**kwargs))

    def load_openapi_spec(self, spec_path: str, base_url: Optional[str] = None):
        """Loads tools directly from an OpenAPI / Swagger spec file."""
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)

        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete"]:
                    continue

                operation_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
                description = details.get("summary", details.get("description", ""))

                # Register basic parameters map
                properties = {}
                required = []
                
                # Extract path/query parameters
                for param in details.get("parameters", []):
                    p_name = param.get("name")
                    properties[p_name] = {
                        "type": param.get("schema", {}).get("type", "string"),
                        "description": param.get("description", "")
                    }
                    if param.get("required"):
                        required.append(p_name)

                schema = {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }

                # Register spec entry (Handler can be routed to an HTTP client core)
                self._schemas.append({
                    "type": "function",
                    "function": {
                        "name": operation_id,
                        "description": f"[{method.upper()} {path}] {description}",
                        "parameters": schema
                    }
                })

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Returns tool schemas ready for LLM function calling formats."""
        return self._schemas

    def _generate_schema_from_func(self, func: Callable, description: str) -> Dict[str, Any]:
        """Internal helper to infer type hints into standard JSON Schema parameters."""
        sig = inspect.signature(func)
        properties = {}
        required = []

        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = type_map.get(param.annotation, "string")
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
  }
          
