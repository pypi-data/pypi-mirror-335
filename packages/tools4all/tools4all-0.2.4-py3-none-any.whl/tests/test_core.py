"""
Tests for the core functionality of Tools4All
"""
import unittest
from unittest.mock import patch, MagicMock

from tools4all import Client, LLMResponseParser


class TestLLMResponseParser(unittest.TestCase):
    """Test the LLMResponseParser class"""
    
    def setUp(self):
        self.parser = LLMResponseParser()
    
    def test_extract_code_blocks(self):
        """Test extracting code blocks from text"""
        text = "Some text\n```python\nprint('hello')\n```\nMore text"
        code_blocks = self.parser.extract_code_blocks(text)
        self.assertEqual(len(code_blocks), 1)
        self.assertEqual(code_blocks[0].language, "python")
        self.assertEqual(code_blocks[0].code, "print('hello')\n")
    
    def test_extract_tool_calls_from_json_block(self):
        """Test extracting tool calls from JSON code blocks"""
        text = "```json\n{\"name\": \"get_weather\", \"arguments\": {\"location\": \"Paris, France\"}}\n```"
        code_blocks = self.parser.extract_code_blocks(text)
        tool_calls = self.parser.extract_tool_calls(text, code_blocks)
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].function.name, "get_weather")
        self.assertEqual(tool_calls[0].function.arguments, {"location": "Paris, France"})
    
    def test_extract_tool_calls_from_tags(self):
        """Test extracting tool calls from <|tool_call|> tags"""
        text = "<|tool_call|>{\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"arguments\":{\"location\":\"Paris, France\"}}}<|/tool_call|>"
        tool_calls = self.parser.extract_tool_calls(text, [])
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].function.name, "get_weather")
        self.assertEqual(tool_calls[0].function.arguments, {"location": "Paris, France"})
    
    def test_extract_comments(self):
        """Test extracting comments from text"""
        text = "This is a comment\n```python\nprint('hello')\n```\nThis is another comment"
        code_blocks = self.parser.extract_code_blocks(text)
        comments = self.parser.extract_comments(text, code_blocks, [])
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0], "This is a comment")
        self.assertEqual(comments[1], "This is another comment")
    
    def test_convert_toolcalls_results(self):
        """Test converting tool call results to a format non-function-calling LLMs can understand"""
        messages = [
            {"role": "user", "content": "What's the weather in Paris?"},
            {"role": "assistant", "content": "I'll check that for you", "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": {"location": "Paris, France"}}}
            ]},
            {"role": "tool", "tool_call_id": "call_1", "name": "get_weather", "content": "Sunny, 22°C"}
        ]
        
        adapted_messages = self.parser.convert_toolcalls_results(messages)
        
        # Check that tool results are converted to user messages
        self.assertEqual(len(adapted_messages), 2)
        self.assertEqual(adapted_messages[0]["role"], "user")
        self.assertEqual(adapted_messages[1]["role"], "user")
        self.assertIn("I've gathered the information you requested", adapted_messages[1]["content"])
        self.assertIn("Get Weather: Sunny, 22°C", adapted_messages[1]["content"])
    
    def test_inject_function_calling_prompt(self):
        """Test injecting function calling prompt for models that don't support tools"""
        messages = [
            {"role": "user", "content": "What's the weather in Paris?"}
        ]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "The city and state"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        adapted_messages = self.parser.inject_function_calling_prompt(messages, tools)
        
        # Check that a system message was added with tool descriptions
        self.assertEqual(len(adapted_messages), 2)
        self.assertEqual(adapted_messages[0]["role"], "system")
        self.assertIn("get_weather", adapted_messages[0]["content"])
        self.assertIn("To use a tool, output a JSON object", adapted_messages[0]["content"])


class TestClient(unittest.TestCase):
    """Test the Client class"""
    
    @patch('ollama.Client')
    def setUp(self, mock_client):
        self.client = Client(host="http://test-host", model="test-model")
        self.mock_ollama = mock_client
    
    def test_init(self):
        """Test Client initialization"""
        # Client inherits from ollama.Client, so it doesn't have a direct host attribute
        # Instead, check the attributes that are set directly in the __init__ method
        self.assertEqual(self.client.model, "test-model")
        self.assertIsInstance(self.client.parser, LLMResponseParser)
        self.assertFalse(self.client.verbose)
    
    @patch('ollama.Client.show')
    def test_get_model_capabilities_with_tools(self, mock_show):
        """Test detecting model capabilities with tools support"""
        # Mock a model that supports tools
        mock_show.return_value = MagicMock(template="This model supports tools")
        
        result = self.client.get_model_capabilities("model-with-tools")
        self.assertTrue(result)
    
    @patch('ollama.Client.show')
    def test_get_model_capabilities_without_tools(self, mock_show):
        """Test detecting model capabilities without tools support"""
        # Mock a model that doesn't support tools - make sure 'tools' is not in the template
        mock_show.return_value = MagicMock(template="This model has no support for function calling")
        
        result = self.client.get_model_capabilities("model-without-tools")
        self.assertFalse(result)
    
    @patch('ollama.Client.chat')
    @patch('tools4all.core.Client.get_model_capabilities')
    def test_chat_with_tools_capable_model(self, mock_capabilities, mock_chat):
        """Test chat method with a model that supports tools"""
        # Mock a model that supports tools
        mock_capabilities.return_value = True
        mock_response = MagicMock()
        mock_chat.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]
        
        response = self.client.chat(
            model="tools-model",
            messages=messages,
            tools=tools
        )
        
        # Check that the parent chat method was called with tools
        mock_chat.assert_called_once()
        call_args = mock_chat.call_args[1]
        self.assertEqual(call_args["model"], "tools-model")
        self.assertEqual(call_args["messages"], messages)
        self.assertEqual(call_args["tools"], tools)
        self.assertEqual(response, mock_response)
    
    @patch('ollama.Client.chat')
    @patch('tools4all.core.Client.get_model_capabilities')
    def test_chat_with_non_tools_capable_model(self, mock_capabilities, mock_chat):
        """Test chat method with a model that doesn't support tools"""
        # Mock a model that doesn't support tools
        mock_capabilities.return_value = False
        
        # Mock the response with tool calls
        mock_response = MagicMock()
        mock_response.message.content = "```json\n{\"name\": \"test_tool\", \"arguments\": {\"arg1\": \"value1\"}}\n```"
        mock_chat.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "arg1": {"type": "string"}
                        },
                        "required": ["arg1"]
                    }
                }
            }
        ]
        
        response = self.client.chat(
            model="no-tools-model",
            messages=messages,
            tools=tools
        )
        
        # Check that the parent chat method was called with adapted messages and no tools
        mock_chat.assert_called_once()
        call_args = mock_chat.call_args[1]
        self.assertEqual(call_args["model"], "no-tools-model")
        self.assertIsNone(call_args["tools"])
        
        # Check that tool calls were parsed from the response
        self.assertTrue(hasattr(response.message, "tool_calls"))


if __name__ == '__main__':
    unittest.main()
