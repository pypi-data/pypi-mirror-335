"""
Core functionality for Tools4All
"""
import json
import re
from typing import List, Dict, Any, Optional

import ollama
from rich import print
from pydantic import BaseModel


class CodeBlocks(BaseModel):
    language: str
    code: str


class Function(BaseModel):
    name: str
    arguments: dict


class ToolCall(BaseModel):
    function: Function


class LLMResponse(BaseModel):
    code_blocks: Optional[List[CodeBlocks]] = None
    tool_calls: Optional[List[ToolCall]] = None
    comments: Optional[List[str]] = None


class LLMResponseParser:
    """
    A parser to extract code blocks, tool calls, and comments from an LLM response.
    """

    CODE_BLOCK_PATTERN = re.compile(
        r'```(?P<lang>[a-zA-Z0-9]*)\n(?P<code>.*?)```', re.DOTALL
    )
    JSON_PATTERN = re.compile(r'\{.*?\}', re.DOTALL)  # Detect JSON anywhere in text

    def parse(self, raw_llm_response: str) -> LLMResponse:
        """
        Parses an LLM response and extracts:
        - Tool calls (using Function & ToolCall models)
        - Code blocks
        - Comments (filtered from system instructions)
        """
        code_blocks = self.extract_code_blocks(raw_llm_response)
        tool_calls = self.extract_tool_calls(code_blocks, raw_llm_response)
        comments = self.extract_comments(raw_llm_response, code_blocks, tool_calls)

        # Remove redundant code blocks if they only contain tool calls
        if code_blocks and tool_calls:
            valid_code_blocks = [
                cb for cb in code_blocks 
                if not self.is_tool_call_json(cb.code)
            ]
            code_blocks = valid_code_blocks

        return LLMResponse(
            code_blocks=code_blocks,
            tool_calls=tool_calls,
            comments=comments
        )

    def extract_code_blocks(self, text: str) -> List[CodeBlocks]:
        """
        Extract code blocks from text.
        """
        code_blocks = []
        for match in self.CODE_BLOCK_PATTERN.finditer(text):
            lang = match.group('lang')
            code = match.group('code')
            code_blocks.append(CodeBlocks(language=lang, code=code))
        return code_blocks

    def extract_tool_calls(self, code_blocks: List[CodeBlocks], text: str) -> List[ToolCall]:
        """
        Extract tool calls from code blocks or directly from text.
        """
        tool_calls = []

        # First try to extract from code blocks
        for cb in code_blocks:
            if cb.language == 'json' or self.is_tool_call_json(cb.code):
                try:
                    data = json.loads(cb.code)
                    if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                        function = Function(name=data['name'], arguments=data['arguments'])
                        tool_calls.append(ToolCall(function=function))
                except json.JSONDecodeError:
                    pass

        # If no tool calls found in code blocks, try to extract from text directly
        if not tool_calls:
            for match in self.JSON_PATTERN.finditer(text):
                json_str = match.group(0)
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                        function = Function(name=data['name'], arguments=data['arguments'])
                        tool_calls.append(ToolCall(function=function))
                except json.JSONDecodeError:
                    pass

        return tool_calls

    def extract_comments(self, text: str, code_blocks: List[CodeBlocks], tool_calls: List[ToolCall]) -> List[str]:
        """
        Extract comments from text, excluding code blocks and tool calls.
        """
        # Remove code blocks from text
        for cb in code_blocks:
            text = text.replace(f"```{cb.language}\n{cb.code}```", "")

        # Remove tool calls from text if they're in JSON format
        for tc in tool_calls:
            json_str = json.dumps(tc.function.model_dump())
            if json_str in text:
                text = text.replace(json_str, "")

        # Split by newlines and filter out empty lines
        comments = [line.strip() for line in text.split('\n') if line.strip()]
        return comments

    def is_tool_call_json(self, text: str) -> bool:
        """
        Check if the given text is a JSON object that represents a tool call.
        """
        try:
            data = json.loads(text)
            if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                return True
            return False
        except json.JSONDecodeError:
            return False


class ToolRegistry:
    """
    A registry for managing available tools and their execution.
    """
    def __init__(self):
        self.tools = {}
        self.tool_definitions = []
    
    def register_tool(self, name, func, description, parameters):
        """
        Register a new tool with the registry.
        
        :param name: The name of the tool
        :param func: The function to execute when the tool is called
        :param description: A description of what the tool does
        :param parameters: The parameters schema for the tool
        """
        self.tools[name] = func
        
        # Create the tool definition
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        
        self.tool_definitions.append(tool_def)
        return tool_def
    
    def run_tool(self, tool_name, arguments):
        """
        Run a registered tool with the given arguments.
        
        :param tool_name: The name of the tool to run
        :param arguments: The arguments to pass to the tool
        :return: The result of running the tool
        """
        if tool_name not in self.tools:
            print(f"Warning: Tool '{tool_name}' not found in registry")
            return f"Error: Tool '{tool_name}' is not available"
        
        try:
            # Get the tool function
            tool_func = self.tools[tool_name]
            
            # Check for required parameters
            tool_def = next((t for t in self.tool_definitions if t["function"]["name"] == tool_name), None)
            if tool_def:
                required_params = tool_def["function"]["parameters"].get("required", [])
                for param in required_params:
                    if param not in arguments:
                        return f"Error: Missing required parameter '{param}'"
            
            # Call the tool function with the arguments
            return tool_func(**arguments)
        except Exception as e:
            print(f"Error executing tool {tool_name}: {str(e)}")
            return f"Error executing tool {tool_name}: {str(e)}"
    
    def get_tool_definitions(self):
        """
        Get the list of tool definitions.
        
        :return: The list of tool definitions
        """
        return self.tool_definitions


class Tools4All(ollama.Client):
    def __init__(self, host: str = 'http://127.0.0.1:11434'):
        super().__init__(host=host)
        self.parser = LLMResponseParser()

    def chat(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> ollama.ChatResponse:
        """
        Chat with the LLM, adapting for models that don't support tools.
        
        :param model: The model to use
        :param messages: The conversation history
        :param tools: The available tools
        :return: The chat response
        """
        try:
            # First try with tools as is
            return super().chat(model=model, messages=messages, tools=tools)
        except Exception as e:
            print(f"[!] Model may not support tool calls: {e}")
            
            # If that fails, try to adapt by injecting system instructions
            adapted_messages = self.adapt_messages_for_tools(messages, tools)
            response = super().chat(model=model, messages=adapted_messages)
            
            # Parse the response to extract tool calls
            parsed = self.parser.parse(response.message.content)
            
            # If tool calls were detected, add them to the response
            if parsed.tool_calls:
                response.message.tool_calls = parsed.tool_calls
            
            return response

    def adapt_messages_for_tools(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Adapt messages for models that don't support tools by injecting system instructions.

        :param messages: The conversation history
        :param tools: The available tools
        :return: The adapted messages
        """
        if not tools:
            return messages

        # Detect existing system message
        user_defined_system_prompt = "You are a helpful assistant."
        system_message_index = None
        
        for i, message in enumerate(messages):
            if message["role"] == "system":
                user_defined_system_prompt = message["content"]
                system_message_index = i
                break

        # Create a system message with tool descriptions
        tool_descriptions = []
        for tool in tools:
            if tool["type"] == "function":
                func = tool["function"]
                tool_descriptions.append(f"""
                Tool: {func["name"]}
                Description: {func["description"]}
                Parameters: {json.dumps(func["parameters"], indent=2)}
                """)

        tool_instructions = f"""
        You have access to the following tools:

        {' '.join(tool_descriptions)}

        To use a tool, output a JSON object with the following structure:
        ```json
        {{
            "name": "tool_name",
            "arguments": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
        ```

        IMPORTANT: For comprehensive responses, use ALL relevant tools when answering a question.

        For EACH tool you want to use, output a separate JSON block like the one shown above. Do not combine multiple tool calls into a single JSON object.

        Make sure to format your response as valid JSON. Do not include any other text or explanation in the JSON blocks.

        ONLY use tools if you need to. If you don't need to use a tool, ignore this instruction and act as a:
        {user_defined_system_prompt}
        to answer the user prompt.
        """

        system_message = {"role": "system", "content": tool_instructions}

        if system_message_index is not None:
            # Replace the existing system message with the new one
            messages[system_message_index] = system_message
        else:
            # Inject system message as the first message
            messages.insert(0, system_message)

        return messages


    def process_prompt(self, prompt: str, registry: ToolRegistry, model: str = 'gemma3:27b'):
        """
        Process a user prompt, handle tool calls, and generate a final answer
        
        :param prompt: The user prompt
        :param registry: The tool registry
        :param model: The model to use for chat completion
        """
        tools = registry.get_tool_definitions()
        
        response: ollama.ChatResponse = self.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            tools=tools
        )
        
        response_content = response.message.content
        # print(response_content)
        
        # Extract tool calls if any, run them and send it back to the model
        if response.message.tool_calls:
            # Create a new messages array that includes the original conversation
            # plus the assistant's response with tool calls and the tool results
            conversation = [
                {
                    'role': 'user',
                    'content': prompt,
                }
            ]
            
            # Create assistant message with tool calls
            tool_calls_data = []
            for i, tool_call in enumerate(response.message.tool_calls):
                tool_call_id = f"call_{i}"
                tool_calls_data.append({
                    'id': tool_call_id,
                    'type': 'function',
                    'function': {
                        'name': tool_call.function.name,
                        'arguments': tool_call.function.arguments
                    }
                })
            
            # Add assistant message with tool calls
            conversation.append({
                'role': 'assistant',
                'content': response.message.content,
                'tool_calls': tool_calls_data
            })
            
            # Collect tool results
            tool_results = []
            
            # Add tool results for each tool call
            for i, tool_call in enumerate(response.message.tool_calls):
                tool_call_id = f"call_{i}"
                # Run the tool using the registry
                result = registry.run_tool(tool_call.function.name, tool_call.function.arguments)
                print(f"Tool result: {result}")
                
                # Store the tool result
                tool_results.append({
                    'name': tool_call.function.name,
                    'result': result
                })
                
                # Add the tool result to the conversation
                conversation.append({
                    'role': 'tool',
                    'tool_call_id': tool_call_id,
                    'name': tool_call.function.name,
                    'content': result
                })
            
            # print("Conversation:")
            # for msg in conversation:
            #     print(f"Role: {msg['role']}")
            #     if 'content' in msg and msg['content']:
            #         print(f"Content: {msg['content']}")
            #     if 'tool_calls' in msg:
            #         print(f"Tool calls: {len(msg['tool_calls'])}")
            #     if 'tool_call_id' in msg:
            #         print(f"Tool call ID: {msg['tool_call_id']}")
            #     if 'name' in msg:
            #         print(f"Tool name: {msg['name']}")
            
            # print("---")
            
            # Generate a final answer based on the tool results
            final_answer = self.generate_final_answer(prompt, tool_results)
            
            # Print the final answer
            # print("\n" + "-"*50)
            # print("FINAL ANSWER:")
            # print("-"*50)
            # print(final_answer)
            # print("-"*50 + "\n")
        else:
            # print("No tool calls detected in the response.")
            pass
    
    def generate_final_answer(self, prompt, tool_results):
        """
        Generate a final answer based on the original prompt and tool results.
        This avoids hallucination by directly using the tool results.
        
        :param prompt: The original user prompt
        :param tool_results: List of tool results
        :return: A formatted final answer
        """
        # Start with a generic response template
        answer = "Based on the information I gathered:\n\n"
        
        # Add each tool result to the answer
        for result in tool_results:
            tool_name = result['name']
            content = result['result']
            
            # Check if the result is an error message
            if content.startswith("Error:"):
                answer += f"• {tool_name}: {content}\n"
            else:
                # For successful results, just include the content directly
                answer += f"{content}\n"
        
        # Add a generic conclusion based on prompt keywords
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in ["weather", "temperature", "humid", "climate"]):
            answer += "\nThis is the current weather information for your requested location."
        elif any(keyword in prompt_lower for keyword in ["search", "find", "look up", "information"]):
            answer += "\nThis information was found based on your search request."
        else:
            answer += "\nI hope this information helps answer your question."
        
        return answer
