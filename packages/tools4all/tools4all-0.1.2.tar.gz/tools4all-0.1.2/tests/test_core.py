"""
Tests for the core functionality of Tools4All
"""
import unittest
from unittest.mock import patch, MagicMock

from tools4all import Tools4All, ToolRegistry, LLMResponseParser


class TestLLMResponseParser(unittest.TestCase):
    """Test the LLMResponseParser class"""
    
    def setUp(self):
        self.parser = LLMResponseParser()
    
    def test_extract_code_blocks(self):
        """Test extracting code blocks from text"""
        # The CODE_BLOCK_PATTERN expects triple backticks, language, newline, code, and triple backticks
        # Make sure the test input matches this exact pattern
        text = "Some text\n```python\nprint('hello')\n```\nMore text"
        code_blocks = self.parser.extract_code_blocks(text)
        self.assertEqual(len(code_blocks), 1)
        self.assertEqual(code_blocks[0].language, "python")
        self.assertEqual(code_blocks[0].code, "print('hello')\n")
    
    def test_extract_tool_calls(self):
        """Test extracting tool calls from code blocks"""
        text = "```json\n{\"name\": \"test_tool\", \"arguments\": {\"arg1\": \"value1\"}}\n```"
        code_blocks = self.parser.extract_code_blocks(text)
        tool_calls = self.parser.extract_tool_calls(code_blocks, text)
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].function.name, "test_tool")
        self.assertEqual(tool_calls[0].function.arguments, {"arg1": "value1"})


class TestToolRegistry(unittest.TestCase):
    """Test the ToolRegistry class"""
    
    def setUp(self):
        self.registry = ToolRegistry()
    
    def test_register_tool(self):
        """Test registering a tool"""
        def test_func(arg1):
            return f"Test: {arg1}"
        
        self.registry.register_tool(
            "test_tool",
            test_func,
            "A test tool",
            {
                "type": "object",
                "properties": {
                    "arg1": {"type": "string"}
                },
                "required": ["arg1"]
            }
        )
        
        self.assertIn("test_tool", self.registry.tools)
        self.assertEqual(len(self.registry.tool_definitions), 1)
    
    def test_run_tool(self):
        """Test running a registered tool"""
        def test_func(arg1):
            return f"Test: {arg1}"
        
        self.registry.register_tool(
            "test_tool",
            test_func,
            "A test tool",
            {
                "type": "object",
                "properties": {
                    "arg1": {"type": "string"}
                },
                "required": ["arg1"]
            }
        )
        
        result = self.registry.run_tool("test_tool", {"arg1": "value1"})
        self.assertEqual(result, "Test: value1")


class TestTools4All(unittest.TestCase):
    """Test the Tools4All class"""
    
    @patch('ollama.Client')
    def setUp(self, mock_client):
        self.client = Tools4All(host="http://test-host")
        self.mock_ollama = mock_client.return_value
    
    def test_adapt_messages_for_tools(self):
        """Test adapting messages for tools"""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
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
        
        adapted_messages = self.client.adapt_messages_for_tools(messages, tools)
        
        # Check that a system message was added
        self.assertEqual(len(adapted_messages), 2)
        self.assertEqual(adapted_messages[0]["role"], "system")
        self.assertIn("test_tool", adapted_messages[0]["content"])


if __name__ == '__main__':
    unittest.main()
