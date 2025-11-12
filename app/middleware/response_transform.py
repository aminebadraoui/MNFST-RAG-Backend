"""
Middleware to transform snake_case to camelCase in API responses
"""
import json
from typing import Any, Dict, List, Union
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class ResponseTransformMiddleware(BaseHTTPMiddleware):
    """
    Middleware to transform snake_case keys to camelCase in JSON responses
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only transform JSON responses
        if (response.headers.get("content-type", "").startswith("application/json") and 
            hasattr(response, 'body')):
            
            try:
                # Parse and transform the response body
                if isinstance(response.body, bytes):
                    body_str = response.body.decode('utf-8')
                else:
                    body_str = response.body
                
                if body_str:
                    body_data = json.loads(body_str)
                    transformed_body = self.transform_keys_to_camel_case(body_data)
                    
                    return Response(
                        content=json.dumps(transformed_body),
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/json"
                    )
            except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
                # If transformation fails, return original response
                pass
        
        return response
    
    def transform_keys_to_camel_case(self, obj: Any) -> Any:
        """
        Recursively transform dictionary keys from snake_case to camelCase
        """
        if isinstance(obj, dict):
            return {
                self.to_camel_case(k): self.transform_keys_to_camel_case(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [self.transform_keys_to_camel_case(item) for item in obj]
        else:
            return obj
    
    def to_camel_case(self, snake_str: str) -> str:
        """
        Convert snake_case string to camelCase
        """
        if not snake_str or '_' not in snake_str:
            return snake_str
        
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])