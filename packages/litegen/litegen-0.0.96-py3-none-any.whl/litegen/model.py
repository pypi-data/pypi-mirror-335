from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal, TypeVar, Generic, Any, Union, Type, get_args, get_origin
import json
import os
import re
from openai import OpenAI
import instructor
from enum import Enum

# Type definitions
ModelType = Literal[
    "smollm2:1.7b-instruct-q4_K_M",
    "smollm2:1.7b-instruct-fp16",
    "smollm2:135m-instruct-fp16",
    "smollm2:135m-instruct-q4_K_M",
    "qwen2.5-coder:1.5b-instruct",
    "qwen2.5-coder:0.5b-instruct",
    "qwen2.5:3b-instruct",
    "qwen2.5:0.5b-instruct",
    "qwen2.5:1.5b-instruct",
    "qwen2.5:7b-instruct",
    "qwen2.5-coder:3b-instruct-q4_k_m",
    "qwen2.5-coder:7b-instruct",
    "qwen2.5-coder:14b-instruct-q4_K_M",
    "qwen2.5-coder:32b-instruct-q4_K_M",
    "llama3.2:1b-instruct-q4_K_M",
    "llama3.2:1b-instruct-fp16",
    "llama3.2:3b-instruct-q4_K_M",
    "llama3.2:3b-instruct-fp16",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "CohereForAI/c4ai-command-r-plus-08-2024",
    "Qwen/QwQ-32B-Preview",
    "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "NousResearch/Hermes-3-Llama-3.1-8B",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "microsoft/Phi-3.5-mini-instruct",
    "exaone3.5:2.4b",
    "gpt-4o-mini",
    "gpt-4o",
    "EXAONE-3.5-2.4B-Instruct-BF16.gguf",
    "EXAONE-3.5-2.4B-Instruct-Q4_K_M.gguf",
    "Llama-3.2-1B-Instruct-f16.gguf",
    "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    "Llama-3.2-1B-Instruct-Q4_K_S.gguf",
    "Llama-3.2-1B-Instruct-Q8_0.gguf",
    "Llama-3.2-3B-Instruct-f16.gguf",
    "qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "qwen2.5-3b-instruct-fp16-00002-of-00002.gguf",
    "qwen2.5-7b-instruct-q4_k_m.gguf",
    "Qwen2.5-0.5B-Instruct-f16.gguf",
    "Qwen2.5-0.5B-Instruct-Q5_K_M.gguf",
    "hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-abliterated-GGUF:Q5_K_M",
    "hf.co/bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF:Q5_K_M"
]

ApiKeyType = Literal[
    "ollama",
    "dsollama",
    "hf_free",
    "huggingchat",
    "huggingchat_nemo",
    "huggingchat_hermes",
    "huggingchat_phimini"
]


class ResponseFormat(str, Enum):
    TEXT = "text"
    STRUCTURE = "structure"
    TOOLS = "tools"
    JSON = "json"


# Response classes
class TextResponse(BaseModel):
    text: str


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolsResponse(BaseModel):
    tool_calls: List[ToolCall]


# Generic for structured responses
T = TypeVar('T', bound=BaseModel)


class SchemaConfig(BaseModel, Generic[T]):
    system_prompt: str
    user_prompt: str
    response_model: Type[T]


# Enhanced LLM class
class BaseLLM:
    def __init__(
        self,
        api_key: ApiKeyType | str | None = None,
        base_url: str = None,
        debug: bool = False,
        instructor_mode: instructor.Mode = instructor.Mode.JSON
    ):
        self.debug = debug
        self._base_api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.api_key = self._get_api_key(api_key)
        self.base_url = self._get_base_url(self.api_key, base_url)
        self.instructor_mode = instructor_mode

        # Default models for different APIs
        self.DEFAULT_MODELS: Dict = {
            "ollama": "qwen2.5:0.5b-instruct",
            "dsollama": "qwen2.5:7b-instruct",
            "hf_free": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "huggingchat": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "huggingchat_nemo": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            "huggingchat_hermes": "NousResearch/Hermes-3-Llama-3.1-8B",
            "huggingchat_phimini": "microsoft/Phi-3.5-mini-instruct",
        }

        # Initialize the clients
        self._update()
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.instructor_client = instructor.from_openai(
            self.client,
            mode=self.instructor_mode
        )

    def _update(self):
        if self._base_api_key == "hf_free":
            self.base_url = "https://api-inference.huggingface.co/v1/"
            self.api_key = "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"

    @staticmethod
    def build_messages(
        system_prompt: str = None,
        prompt: str = "",
        context: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build messages list from components."""
        _messages = []

        # Add system prompt if provided
        if system_prompt:
            _messages.append({"role": "system", "content": system_prompt})

        # Add context (previous conversation) if provided
        if context:
            _messages.extend(context)

        # Add current prompt if provided
        if prompt:
            _messages.append({"role": "user", "content": prompt})

        return _messages

    @staticmethod
    def handle_str_messages(messages, system_prompt):
        """Handle string messages and build them into a list of messages."""
        _messages = []
        if system_prompt:
            _messages.append({"role": "system", "content": system_prompt})

        _messages.append({"role": "user", "content": messages})

        return _messages

    def _get_base_url(self, api_key, base_url):
        if base_url:
            return base_url

        if 'huggingchat' in str(api_key):
            _api_key = "huggingchat"  # Match huggingchat_code etc..
        else:
            _api_key = api_key

        match str(_api_key):
            case 'dsollama':
                return "http://192.168.170.76:11434/v1"
            case 'ollama':
                return "http://localhost:11434/v1"
            case 'huggingchat':
                return "http://localhost:11437/v1"
            case 'llamacpp':
                return "http://localhost:11438/v1"
            case _:
                if os.environ.get('OPENAI_BASE_URL', None):
                    return os.environ['OPENAI_BASE_URL']
                return None

    def _get_api_key(self, api_key: str | None = None) -> str:
        if api_key:
            return api_key
        _env_api_key = os.environ.get('OPENAI_API_KEY')
        if _env_api_key:
            return _env_api_key
        return "dummy-key"  # Fallback for services that need a key but don't use it

    def _get_model_name(self):
        model = os.environ.get('OPENAI_MODEL_NAME')
        if model is None:
            model = self.DEFAULT_MODELS.get(self._base_api_key, None)
            if model is None:
                raise ValueError("Missing required environment variable: OPENAI_MODEL_NAME or pass model parameter")
        return model

    def _prepare_tools(self, tools):
        """Convert functions to OpenAI tool format if needed"""
        from ollama._utils import convert_function_to_tool
        return [t if isinstance(t, dict) else convert_function_to_tool(t) for t in tools]

    def sanitize_json_string(self, json_str: str) -> str:
        """
        Sanitizes a JSON-like string by handling both Python dict format and JSON format
        with special handling for code snippets and control characters.
        """
        # Remove any leading/trailing whitespace and triple quotes
        json_str = json_str.strip().strip('"""').strip("'''")

        # Pre-process: convert Python dict style to JSON if needed
        if json_str.startswith("{'"):  # Python dict style
            # Handle Python dict-style strings
            def replace_dict_quotes(match):
                content = match.group(1)
                # Escape any double quotes in the content
                content = content.replace('"', '\\"')
                return f'"{content}"'

            # Convert Python single-quoted strings to double-quoted
            pattern = r"'([^'\\]*(?:\\.[^'\\]*)*)'"
            json_str = re.sub(pattern, replace_dict_quotes, json_str)

            # Handle Python boolean values
            json_str = json_str.replace("True", "true")
            json_str = json_str.replace("False", "false")

        # Process code snippets and strings with control characters
        def escape_special_content(match):
            content = match.group(1)

            # Handle newlines and control characters
            if '\n' in content or '\\n' in content:
                # Properly escape newlines and maintain indentation
                content = content.replace('\\n', '\n')  # Convert literal \n to newline
                # Now escape all control characters properly
                content = json.dumps(content)[1:-1]  # Use json.dumps but remove outer quotes

            return f'"{content}"'

        # Find and process all quoted strings, handling escaped quotes
        pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
        processed_str = re.sub(pattern, escape_special_content, json_str)

        try:
            # Try to parse and re-serialize to ensure valid JSON
            return json.dumps(json.loads(processed_str))
        except json.JSONDecodeError as e:
            # If direct parsing fails, try to fix common issues
            try:
                # Try to handle any remaining unescaped control characters
                cleaned = processed_str.encode('utf-8').decode('unicode-escape')
                return json.dumps(json.loads(cleaned))
            except Exception as e:
                raise ValueError(f"Failed to create valid JSON: {str(e)}")

    def text_completion(
        self,
        system_prompt: str = None,
        prompt: str = "",
        model: ModelType = None,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> TextResponse:
        """Generate a text response"""
        if model is None:
            model = self._get_model_name()

        messages = self.build_messages(system_prompt, prompt, context)

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            stop=stop,
            **kwargs
        )

        if stream:
            return self._handle_streaming_response(response)
        else:
            content = response.choices[0].message.content
            return TextResponse(text=content)

    def tool_completion(
        self,
        system_prompt: str = None,
        prompt: str = "",
        model: ModelType = None,
        tools: List = None,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> ToolsResponse:
        """Generate a response using tools"""
        if model is None:
            model = self._get_model_name()

        if tools is None:
            raise ValueError("Tools must be provided for tool completion")

        tools = self._prepare_tools(tools)
        messages = self.build_messages(system_prompt, prompt, context)

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            **kwargs
        )

        # Extract tool calls from response
        tool_calls = []
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except:
                    arguments = {}

                tool_calls.append(ToolCall(
                    name=tool_call.function.name,
                    arguments=arguments
                ))

        return ToolsResponse(tool_calls=tool_calls)

    def structured_completion(
        self,
        schema: Union[SchemaConfig, BaseModel],
        model: ModelType = None,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Generate a structured response using Pydantic schema"""
        if model is None:
            model = self._get_model_name()

        # Handle both SchemaConfig and direct BaseModel
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            # Just a response model without prompts
            response_model = schema
            system_prompt = kwargs.pop('system_prompt', None)
            prompt = kwargs.pop('prompt', "")
        elif isinstance(schema, SchemaConfig):
            # Full schema config
            system_prompt = schema.system_prompt
            prompt = schema.user_prompt
            response_model = schema.response_model
        elif isinstance(schema, BaseModel):
            # Handle if SchemaConfig was instantiated
            if hasattr(schema, 'system_prompt') and hasattr(schema, 'user_prompt') and hasattr(schema,
                                                                                               'response_model'):
                system_prompt = schema.system_prompt
                prompt = schema.user_prompt
                response_model = schema.response_model
            else:
                raise ValueError("Schema must be a SchemaConfig or a BaseModel response type")
        else:
            raise ValueError("Schema must be a SchemaConfig or a BaseModel response type")

        messages = self.build_messages(system_prompt, prompt, context)

        # Use instructor for structured output
        result = self.instructor_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_model=response_model,
            **kwargs
        )

        return result

    def _handle_streaming_response(self, stream_response):
        """Handle streaming responses by collecting chunks into a full response"""
        chunks = []
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                chunks.append(chunk.choices[0].delta.content)
                # Optionally print the chunk
                if self.debug:
                    print(chunk.choices[0].delta.content, end="", flush=True)

        return TextResponse(text="".join(chunks))

    def __call__(
        self,
        prompt: str = "",
        system_prompt: str = None,
        format: ResponseFormat = ResponseFormat.TEXT,
        schema: Union[SchemaConfig, BaseModel, Type[BaseModel]] = None,
        tools: List = None,
        model: str = "smollm2:1.7b-instruct-q4_K_M",
        context: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = 0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Union[TextResponse, ToolsResponse, Any]:
        """
        Unified entry point that routes to the appropriate completion method
        based on format argument
        """
        # Determine response format
        if schema is not None:
            format = ResponseFormat.STRUCTURE
        elif tools is not None:
            format = ResponseFormat.TOOLS

        # Route to appropriate method
        if format == ResponseFormat.TEXT:
            return self.text_completion(
                system_prompt=system_prompt,
                prompt=prompt,
                model=model,
                context=context,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                stop=stop,
                **kwargs
            )
        elif format == ResponseFormat.STRUCTURE:
            return self.structured_completion(
                schema=schema,
                model=model,
                context=context,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                prompt=prompt,
                **kwargs
            )
        elif format == ResponseFormat.TOOLS:
            return self.tool_completion(
                system_prompt=system_prompt,
                prompt=prompt,
                model=model,
                tools=tools,
                context=context,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                **kwargs
            )
        elif format == ResponseFormat.JSON:
            # Handle raw JSON response
            if model is None:
                model = self._get_model_name()

            messages = self.build_messages(system_prompt, prompt, context)
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                **kwargs
            )

            return json.loads(response.choices[0].message.content)
        else:
            raise ValueError(f"Unsupported response format: {format}")

    def print_stream(self, *args, **kwargs):
        """Utility method to print streaming output"""
        kwargs['stream'] = True
        kwargs['debug'] = True
        return self.text_completion(*args, **kwargs)


# Convenience child classes
class DSEnhancedLLM(BaseLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(api_key='dsollama', *args, **kwargs)


class HFEnhancedLLM(BaseLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(api_key='huggingchat', *args, **kwargs)


class LLM(BaseLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(api_key='ollama', *args, **kwargs)


# Example usage functions
def example_text_completion():
    llm = LLM()
    response = llm(
        prompt="Tell me a joke about programming",
        system_prompt="You are a helpful assistant.",
        model="smollm2:1.7b-instruct-q4_K_M"
    )
    print(f"Text response: {response.text}")


def example_tools_completion():
    from typing import Dict, List, Any

    def search_web(query: str) -> List[Dict[str, str]]:
        """Search the web for information"""
        # Placeholder function
        return [{"title": "Example result", "url": "https://example.com", "snippet": "Example snippet"}]

    def calculate(expression: str) -> float:
        """Calculate a mathematical expression"""
        # Placeholder function
        return eval(expression)

    llm = LLM()
    response = llm(
        prompt="What is 25 * 4?",
        system_prompt="You are a helpful assistant. Use tools when appropriate.",
        model="smollm2:1.7b-instruct-q4_K_M",
        tools=[calculate, search_web]
    )

    print(f"Tool calls: {response.tool_calls}")

    response = llm(
        prompt="What is 25 * 4 and weather in gurgaon?",
        system_prompt="You are a helpful assistant. Use tools when appropriate.",
        model="smollm2:1.7b-instruct-q4_K_M",
        tools=[calculate, search_web]
    )

    print(f"Tool calls: {response.tool_calls}")


def example_structured_completion():
    from pydantic import BaseModel, Field

    class PlanningSteps(BaseModel):
        steps: List[str] = Field(..., description="List of steps to complete the task")

    system_prompt = """You are a Planner Agent, understand the user request and return a list of steps."""

    llm = LLM()

    # Method 2: Direct schema with separate prompts
    response2 = llm(
        system_prompt=system_prompt,
        prompt="How do I plant a garden?",
        model="smollm2:1.7b-instruct-q4_K_M",
        schema=PlanningSteps
    )
    print(f"Structured response method 2: {response2.steps}")


if __name__ == "__main__":
    example_text_completion()
    # example_tools_completion()
    # example_structured_completion()