import json
import re
from typing import List, Optional, Dict, Any
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
    # Simple pattern to find potential JSON objects
    JSON_START_PATTERN = re.compile(r'(\{)', re.DOTALL)
    # Pattern to find tool calls enclosed in <|tool_call|> tags
    TOOL_CALL_PATTERN = re.compile(r'<\|tool_call\|>(.*?)<\|/tool_call\|>', re.DOTALL)

    def parse(self, raw_llm_response: str) -> LLMResponse:
        """
        Parses an LLM response and extracts:
        - Tool calls (using Function & ToolCall models)
        - Code blocks
        - Comments (filtered from system instructions)
        """
        code_blocks = self.extract_code_blocks(raw_llm_response)
        tool_calls = self.extract_tool_calls(raw_llm_response, code_blocks)
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

    def extract_tool_calls(self, text: str, code_blocks: List[CodeBlocks]) -> List[ToolCall]:
        """
        Extract tool calls from text in various formats:
        1. <|tool_call|> tags format
        2. JSON code blocks
        3. Inline JSON
        """
        tool_calls = []
        
        # 1. Extract from <|tool_call|> tags
        for match in self.TOOL_CALL_PATTERN.finditer(text):
            tool_call_content = match.group(1).strip()
            try:
                data = json.loads(tool_call_content)
                
                # Handle array of tool calls
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('type') == 'function':
                            func_data = item.get('function', {})
                            if 'name' in func_data and 'arguments' in item:
                                function = Function(
                                    name=func_data['name'],
                                    arguments=item['arguments']
                                )
                                tool_calls.append(ToolCall(function=function))
                
                # Handle single tool call
                elif isinstance(data, dict) and data.get('type') == 'function':
                    func_data = data.get('function', {})
                    if 'name' in func_data and 'arguments' in data:
                        function = Function(
                            name=func_data['name'],
                            arguments=data['arguments']
                        )
                        tool_calls.append(ToolCall(function=function))
            except json.JSONDecodeError:
                pass
        
        # If we found tool calls in the tags, return them
        if tool_calls:
            return tool_calls
        
        # 2. Extract from code blocks
        for cb in code_blocks:
            if cb.language == 'json' or not cb.language:
                try:
                    data = json.loads(cb.code)
                    if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                        function = Function(name=data['name'], arguments=data['arguments'])
                        tool_calls.append(ToolCall(function=function))
                except json.JSONDecodeError:
                    pass
        
        # If we found tool calls in code blocks, return them
        if tool_calls:
            return tool_calls
        
        # 3. Extract from inline JSON
        json_objects = self.find_json_objects(text)
        for json_str in json_objects:
            try:
                data = json.loads(json_str)
                if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                    function = Function(name=data['name'], arguments=data['arguments'])
                    tool_calls.append(ToolCall(function=function))
            except json.JSONDecodeError:
                pass
        
        return tool_calls
    
    def find_json_objects(self, text: str) -> List[str]:
        """
        Find all potential JSON objects in text by balancing braces.
        This is more robust than using regex for nested JSON structures.
        """
        json_objects = []
        start_positions = [match.start() for match in self.JSON_START_PATTERN.finditer(text)]
        
        for start_pos in start_positions:
            # Try to find a complete JSON object starting at this position
            brace_count = 0
            in_string = False
            escape_char = False
            
            for i in range(start_pos, len(text)):
                char = text[i]
                
                # Handle string literals
                if char == '"' and not escape_char:
                    in_string = not in_string
                
                # Handle escape characters in strings
                if in_string and char == '\\' and not escape_char:
                    escape_char = True
                    continue
                escape_char = False
                
                # Only count braces outside of string literals
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        
                        # If we've balanced all braces, we've found a complete JSON object
                        if brace_count == 0:
                            json_objects.append(text[start_pos:i+1])
                            break
        
        return json_objects

    def extract_comments(self, text: str, code_blocks: List[CodeBlocks], tool_calls: List[ToolCall]) -> List[str]:
        """
        Extract comments from text, excluding code blocks and tool calls.
        """
        # Make a copy of the text to avoid modifying the original
        filtered_text = text
        
        # Remove code blocks from text
        for cb in code_blocks:
            filtered_text = filtered_text.replace(f"```{cb.language}\n{cb.code}```", "")
            # Also try without newlines (for compact code blocks)
            filtered_text = filtered_text.replace(f"```{cb.language}{cb.code}```", "")

        # Remove tool calls from text if they're in JSON format
        for tc in tool_calls:
            # Try different JSON formats that might be in the text
            function_data = tc.function.model_dump()
            
            # Standard JSON format with name and arguments
            json_str = json.dumps({"name": tc.function.name, "arguments": tc.function.arguments})
            if json_str in filtered_text:
                filtered_text = filtered_text.replace(json_str, "")
            
            # Compact JSON format (no spaces)
            compact_json = json_str.replace(" ", "")
            if compact_json in filtered_text:
                filtered_text = filtered_text.replace(compact_json, "")
            
            # Pretty-printed JSON format
            pretty_json = json.dumps({"name": tc.function.name, "arguments": tc.function.arguments}, indent=4)
            if pretty_json in filtered_text:
                filtered_text = filtered_text.replace(pretty_json, "")
        
        # Remove tool calls enclosed in <|tool_call|> tags
        filtered_text = re.sub(self.TOOL_CALL_PATTERN, "", filtered_text)
        
        # Remove any remaining JSON objects that look like tool calls
        json_objects = self.find_json_objects(filtered_text)
        for json_str in json_objects:
            try:
                data = json.loads(json_str)
                if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                    filtered_text = filtered_text.replace(json_str, "")
            except json.JSONDecodeError:
                pass
        
        # Clean up any leftover empty code block markers
        filtered_text = re.sub(r'```[a-zA-Z0-9]*```', '', filtered_text)

        # Split by newlines and filter out empty lines
        comments = [line.strip() for line in filtered_text.split('\n') if line.strip()]
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

    def convert_toolcalls_results(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert 'tool' role messages into 'user' role messages for models that don't support tool calls.
        This function transforms tool call results into a format that non-function-calling LLMs can understand.
        
        :param messages: The conversation history including tool call results
        :return: The adapted messages with tool results converted to user messages
        """
        if not messages:
            return messages
        
        # Create a new messages list
        adapted_messages = []
        tool_results = []
        
        # Track the last user message to provide context
        last_user_message = None
        
        for message in messages:
            if message["role"] == "tool":
                # Collect tool results but don't add them directly to adapted_messages
                tool_name = message.get("name", "unknown_tool")
                tool_result = message.get("content", "No result")
                tool_results.append({
                    "name": tool_name,
                    "result": tool_result
                })
            elif message["role"] == "user":
                # Add user messages directly and track the last one
                adapted_messages.append(message)
                last_user_message = message
            elif message["role"] == "system":
                # Add system messages directly
                adapted_messages.append(message)
            elif message["role"] == "assistant" and "tool_calls" in message:
                # Skip assistant messages with tool_calls as they'll be represented by the tool results
                continue
            else:
                # Add any other message types directly
                adapted_messages.append(message)
        
        # If we collected tool results, add a new user message with the results
        if tool_results and last_user_message:
            # Format the tool results into a user-friendly message
            tool_results_content = "I've gathered the information you requested:\n\n"
            
            for result in tool_results:
                tool_name = result["name"].replace("_", " ").title()
                tool_result = result["result"]
                tool_results_content += f"- {tool_name}: {tool_result}\n"
            
            tool_results_content += "\nPlease provide a comprehensive response based on this information."
            
            # Add the formatted tool results as a new user message
            adapted_messages.append({
                "role": "user",
                "content": tool_results_content
            })
        
        return adapted_messages

    def inject_function_calling_prompt(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
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


if __name__ == "__main__":
    
    texts = [
        """<|tool_call|>[{"type":"function","function":{"name":"get_weather","description":"Get the current weather","parameters":{"type":"object","required":["location"],"properties":{"location":{"type":"string","description":"The city and state, e.g., San Francisco, CA"}}}},"arguments":{"location":"Paris, France"}}]<|/tool_call|>""",
        """{"name":"get_weather","arguments":{"location":"Paris, France"}}""",
        """```json{"name":"get_weather","arguments":{"location":"Paris, France"}}```""",
        """
        ```json
        {
            "name":"get_weather",
            "arguments":{
                "location":"Paris, France"
            }
        }
        ```
        """,
        """
        Here is the JSON:

        ```json
        {
            "name":"get_weather",
            "arguments":{
                "location":"Paris, France",
                "units":"°C"
            }
        }
        ```

        This tools should be used to get the current weather.
        """,
    ]
    
    parser = LLMResponseParser()
    for i, text in enumerate(texts):
        print(f"\nTest {i+1}:")
        print("Input text:", text)
        
        result = parser.parse(text)
        print("Parsed result:")
        if result.code_blocks:
            print("Code blocks:", [f"{cb.language}: {cb.code}" for cb in result.code_blocks])
        else:
            print("Code blocks: []")
            
        if result.tool_calls:
            print("Tool calls:", [f"{tc.function.name}({tc.function.arguments})" for tc in result.tool_calls])
        else:
            print("Tool calls: []")
            
        if result.comments:
            print("Comments:", result.comments)
        else:
            print("Comments: []")
            
        print("-" * 50)