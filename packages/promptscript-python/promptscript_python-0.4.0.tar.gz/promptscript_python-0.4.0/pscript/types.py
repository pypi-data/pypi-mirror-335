# pscript/types.py

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, Type, Annotated
from pydantic import BaseModel, Field, ConfigDict

@dataclass
class ExecutionContext:
    """
    Represents the execution context for a function or section of code.
    Used to track the flow of execution across function calls and threads.
    """
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_context_id: Optional[str] = None
    context_path: list[str] = field(default_factory=lambda: ["root"])
    name: str = "root"
    thread_id: int = field(default_factory=threading.get_ident)
    
    def create_child_context(self, name: Optional[str] = None) -> 'ExecutionContext':
        """
        Create a child context that inherits from this context.
        """
        from .tracer import get_global_tracer
        
        child_id = str(uuid.uuid4())
        child_name = name or f"child_{child_id[:8]}"
        
        # Create new path by appending to the parent's path
        child_path = self.context_path.copy()
        child_path.append(f"{self.name}/{child_name}")
        
        new_context = ExecutionContext(
            context_id=child_id,
            parent_context_id=self.context_id,
            context_path=child_path,
            name=child_name,
            thread_id=threading.get_ident()
        )
        
        # Register with the tracer
        tracer = get_global_tracer()
        with tracer._contexts_lock:
            tracer._contexts[new_context.context_id] = new_context
            
        return new_context
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary representation.
        """
        return {
            "context_id": self.context_id,
            "parent_context_id": self.parent_context_id,
            "context_path": self.context_path,
            "name": self.name,
            "thread_id": self.thread_id
        }
    
@dataclass
class Attachment:
    data: bytes
    mime_type: str
    name: Optional[str] = None

@dataclass
class FunctionMetadata:
    nested_functions: Dict[str, Tuple[str, Callable]]
    param_name: Optional[str]
    param_type: Type  
    return_type: Type
    decorator_type: str
    function_name: str
    template_lineno: Optional[int] = None
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    final_config: Optional["FunctionConfig"] = None

class FunctionConfig(BaseModel):
    model: str = Field(
        default="azure_openai/gpt-4o-mini", 
        description="Which model to call, e.g. anthropic/claude-2, azure_openai/gpt-4o-mini, etc."
    )
    temperature: Annotated[
        float, 
        Field(ge=0.0, le=2.0, description="Sampling temperature for the model")
    ] = 0.7
    max_tokens: Annotated[
        int, 
        Field(ge=1, le=16384, description="Max tokens for the completion")
    ] = 2048
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to prefix the conversation"
    )
    max_function_calls: Optional[int] = Field(default=None)
    authentication: Optional[str] = Field(
        default=None,
        description="Authentication method for Azure OpenAI. Options are 'token' or 'managed' (default)."
    )
    # New fields for Azure OpenAI
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Azure OpenAI, e.g. '2024-08-01-preview'"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for the API endpoint, e.g. 'https://example.openai.azure.com'"
    )
    deployment_name: Optional[str] = Field(
        default=None,
        description="Deployment name for Azure OpenAI"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the service (if using token-based authentication)"
    )
    # Azure OpenAI specific configuration (can be passed directly)
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint URL (alternative to AZURE_OPENAI_ENDPOINT env var)"
    )
    azure_openai_deployment: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name (alternative to AZURE_OPENAI_DEPLOYMENT env var)"
    )
    azure_openai_api_version: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API version (alternative to AZURE_OPENAI_API_VERSION env var)"
    )
    model_config = ConfigDict(
        protected_namespaces=()
    )

@dataclass
class ModelMetadata:
    model_name: str
    temperature: float
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_ms: Optional[float] = None

class ExecutionEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    start_timestamp: datetime = Field(default_factory=datetime.now)
    end_timestamp: Optional[datetime] = None
    session_id: str
    function_name: str
    result: Optional[Any] = None  
    duration_ms: Optional[float] = None  
    error: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)  
    parent_event_id: Optional[str] = None
    child_event_ids: list[str] = Field(default_factory=list)
    messages_to_llm: Optional[list[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None  # Added field for response format
    functions: Optional[list[Dict[str, Any]]] = None  # Added field for functions
    llm_response: Optional[Dict[str, Any]] = None  
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    request_duration_ms: Optional[float] = None  
    context_id: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            bytes: lambda x: {
                '_type': 'binary',
                'data': x.hex(),
                'size': len(x)
            }
        }
    )

    def add_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def add_child_event(self, child_id: str) -> None:
        if child_id not in self.child_event_ids:
            self.child_event_ids.append(child_id)
    
    def add_response_format(self, response_format: Dict[str, Any]) -> None:
        """Add structured output schema information"""
        self.response_format = response_format
    
    def add_functions(self, functions: list[Dict[str, Any]]) -> None:
        """Add function definitions"""
        self.functions = functions
            
    @classmethod
    def model_validate_json(cls, json_data: str, **kwargs) -> 'ExecutionEvent':
        data = super().model_validate_json(json_data, **kwargs)
        # Handle binary data deserialization if needed
        if isinstance(data.input_data, dict) and data.input_data.get('_type') == 'binary':
            data.input_data = bytes.fromhex(data.input_data['data'])
        if isinstance(data.output_data, dict) and data.output_data.get('_type') == 'binary':
            data.output_data = bytes.fromhex(data.output_data['data'])
        return data

class BinaryData(BaseModel):
    data: bytes
    size: int
    mime_type: Optional[str] = None

class TraceFile(BaseModel):
    session_id: str
    module_name: str
    created_at: datetime
    updated_at: datetime
    events: list[ExecutionEvent] = Field(default_factory=list)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

class ResponseMetadata(BaseModel):
    """Metadata about a model response, including token counts and other performance metrics."""
    
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    latency_ms: Optional[float] = None
    
    model_name: Optional[str] = None
    provider: Optional[str] = None
    
    raw_provider_data_str: Optional[str] = None
    
    provider_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    def as_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the metadata."""
        return {k: v for k, v in self.model_dump().items() if v is not None}