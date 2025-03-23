from typing import Any, Optional, Union, Iterator, Mapping, Sequence
import ollama
from rich import print
from pydantic.json_schema import JsonSchemaValue
from .llm_parser import LLMResponseParser

class Client(ollama.Client):
    def __init__(self, host: str = 'http://127.0.0.1:11434', model: str = None, verbose: bool = False):
        super().__init__(host=host)
        self.parser = LLMResponseParser()
        self.verbose = verbose
        self.model = model

    def get_model_capabilities(self, model: str = None) -> bool:
        # Use default model if none provided
        if model is None:
            model = self.model
        # Check if model supports tools
        capable_tools = False
        show_response = self.show(model=model)
        result = str(show_response.template).lower()
        if 'tools' in result:
            capable_tools = True
        return capable_tools

    def chat(
        self,
        model: str = None,
        messages: Optional[Sequence[Union[Mapping[str, Any], ollama.Message]]] = None,
        *,
        tools: Optional[Sequence[Union[Mapping[str, Any], ollama.Tool, callable]]] = None,
        stream: bool = False,
        format: Optional[Union[str, JsonSchemaValue]] = None,
        options: Optional[Union[Mapping[str, Any], ollama.Options]] = None,
        keep_alive: Optional[Union[float, str]] = None,
    ) -> Union[ollama.ChatResponse, Iterator[ollama.ChatResponse]]:
        """
        Chat with the LLM, adapting for models that don't support tools.

        :param model: The model to use
        :param messages: The conversation history
        :param tools: The available tools
        :param stream: Whether to stream responses
        :param format: Response format (e.g., 'json')
        :param options: Additional Ollama options (e.g., temperature, max_tokens)
        :param keep_alive: Keep connection alive for faster subsequent queries
        :return: The chat response (or an iterator if streaming)
        """
        # Use default model if none provided
        if model is None:
            model = self.model

        # Check if model supports tools
        capable_tools = self.get_model_capabilities(model)
        if self.verbose:
            print(f"Model {model} supports tools: {capable_tools}")

        if capable_tools:
            try:
                # First attempt with original settings
                return super().chat(
                    model=model,
                    messages=messages,
                    tools=tools,
                    stream=stream,
                    format=format,
                    options=options,
                    keep_alive=keep_alive
                )
            except Exception as e:
                print(str(e))
                raise
        else: # model may not support tools
            try:
                # Convert tool results to a format the model can understand
                messages = self.parser.convert_toolcalls_results(messages)
                
                # if tools are required
                if tools is not None and len(tools) > 0:
                    
                    # FUNCTION CALLING system instructions
                    adapted_messages = self.parser.inject_function_calling_prompt(messages, tools)
                    response = super().chat(
                        model=model,
                        messages=adapted_messages,
                        tools=None,  # Remove tools since model doesn't support them
                        stream=False,
                        format=None,
                        options=options,
                        keep_alive=keep_alive
                    )

                    # Parse response to extract tool calls
                    parsed = self.parser.parse(response.message.content)

                    # If tool calls were detected, modify response
                    if parsed.tool_calls:
                        response.message.tool_calls = parsed.tool_calls
                        response.message.content = "\n".join(parsed.comments)

                    return response

                else: # no tools required
                    return super().chat(
                        model=model,
                        messages=messages,
                        tools=None,
                        stream=stream,
                        format=format,
                        options=options,
                        keep_alive=keep_alive
                    )
            except Exception as e:
                print(str(e))
                raise
