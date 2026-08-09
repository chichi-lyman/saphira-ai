import json
from typing import Callable, Dict, Any

class PluginRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: list[Dict[str, Any]] = []

    def register_tool(self, name: str, description: str, schema: dict):
        """Decorator or function to register custom tools dynamically."""
        def decorator(func: Callable):
            self._tools[name] = func
            self._schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": schema
                }
            })
            return func
        return decorator

    def execute(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' is not registered.")
        return self._tools[tool_name](**kwargs)

    def get_schemas(self) -> list[Dict[str, Any]]:
        return self._schemas

