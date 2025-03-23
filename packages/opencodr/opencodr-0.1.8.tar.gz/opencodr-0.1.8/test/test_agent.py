import unittest
import asyncio
import json
import pytest
from litellm import Choices, Message, ModelResponse
from unittest.mock import AsyncMock, MagicMock, patch

from mcp import Tool
from opencodr.agent import Agent
from opencodr.config import OpenCoderConfig
from opencodr.mcp_client import Server
from opencodr.types import ToolCallError
from mcp.types import TextContent


class TestAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_config = OpenCoderConfig(OC_MODEL="openai/gpt-4o")

        self.mock_server = MagicMock(spec=Server)
        self.mock_tool = MagicMock(spec=Tool)

        self.patcher = patch(
            "opencodr.agent.supports_function_calling", return_value=True
        )
        self.mock_supports_function_calling = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        self.get_opencoder_dir_patcher = patch(
            "opencodr.agent.get_opencoder_dir", return_value=None
        )
        self.mock_get_opencoder_dir = self.get_opencoder_dir_patcher.start()
        self.addCleanup(self.get_opencoder_dir_patcher.stop)

    @pytest.mark.asyncio
    async def test_cleanup_servers_calls_all_server_cleanups(self):
        mock_server1 = MagicMock(spec=Server)
        mock_server1.cleanup = MagicMock(return_value=asyncio.Future())
        mock_server1.cleanup.return_value.set_result(None)

        mock_server2 = MagicMock(spec=Server)
        mock_server2.cleanup = MagicMock(return_value=asyncio.Future())
        mock_server2.cleanup.return_value.set_result(None)

        mock_server3 = MagicMock(spec=Server)
        mock_server3.cleanup = MagicMock(return_value=asyncio.Future())
        mock_server3.cleanup.return_value.set_result(None)

        agent = Agent(conf=self.mock_config)
        agent.mcp_servers = [mock_server1, mock_server2, mock_server3]

        await agent.cleanup_servers()

        mock_server1.cleanup.assert_called_once()
        mock_server2.cleanup.assert_called_once()
        mock_server3.cleanup.assert_called_once()

    def test_init_with_default_parameters(self):
        agent = Agent(conf=self.mock_config)
        self.assertEqual(len(agent.messages), 1)
        self.assertEqual(agent.messages[0].role, "system")
        self.assertEqual(agent.messages[0].content, Agent.SYSTEM_MESSAGE_TEMPLATE)
        self.assertEqual(agent.allow_tool_use, True)
        self.assertEqual(agent.mcp_servers, [])

    def test_init_with_custom_messages(self):
        custom_messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi"),
        ]
        agent = Agent(conf=self.mock_config, messages=custom_messages)

        self.assertEqual(len(agent.messages), 2)
        self.assertEqual(agent.messages[0].role, "user")
        self.assertEqual(agent.messages[0].content, "Hello")
        self.assertEqual(agent.messages[1].role, "assistant")
        self.assertEqual(agent.messages[1].content, "Hi")
        self.assertNotEqual(agent.messages[0].role, "system")

    def test_init_with_custom_servers(self):
        mock_server1 = MagicMock(spec=Server)
        mock_server2 = MagicMock(spec=Server)
        servers = [mock_server1, mock_server2]

        agent = Agent(conf=self.mock_config, mcp_servers=servers)
        self.assertEqual(agent.mcp_servers, servers)

    def test_init_with_null_config(self):
        with self.assertRaises(ValueError) as context:
            Agent(conf=None)
        self.assertEqual(str(context.exception), "config required")

    @patch("os.listdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_init_loads_custom_system_message(self, mock_open, mock_listdir):
        self.mock_get_opencoder_dir.return_value = "/fake/path"
        mock_listdir.return_value = ["system.txt", "other.txt"]
        mock_open().read.side_effect = ["Custom system message"]

        agent = Agent(conf=self.mock_config)

        self.assertEqual(agent.messages[0].content, "Custom system message")
        mock_open.assert_called_with("/fake/path/system.txt", "r", encoding="utf-8")

    @patch("os.listdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_init_loads_custom_reprompt_message(self, mock_open, mock_listdir):
        self.mock_get_opencoder_dir.return_value = "/fake/path"
        mock_listdir.return_value = ["reprompt.txt", "other.txt"]
        mock_open().read.side_effect = ["Custom reprompt message"]

        agent = Agent(conf=self.mock_config)

        self.assertEqual(agent.REPROMPT_MESSAGE_TEMPLATE, "Custom reprompt message")
        mock_open.assert_called_with("/fake/path/reprompt.txt", "r", encoding="utf-8")

    def test_function_calling_disabled_by_model(self):
        self.mock_supports_function_calling.return_value = False

        agent = Agent(conf=self.mock_config)
        self.assertEqual(agent.allow_tool_use, False)

    @pytest.mark.asyncio
    async def test_exec_tool_call_successful(self):
        agent = Agent(conf=self.mock_config)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "test-tool-call-id"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"param1": "value1"}'

        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool description"

        mock_server = MagicMock(spec=Server)

        mock_result = MagicMock()
        mock_result.isError = False

        mock_text = TextContent(type="text", text="Test result", annotations=None)
        mock_result.content = [mock_text]

        mock_server.execute_tool = MagicMock(return_value=asyncio.Future())
        mock_server.execute_tool.return_value.set_result(mock_result)

        agent.tools = [(mock_tool, mock_server)]

        result = await agent.exec_tool_call(mock_tool_call)

        mock_server.execute_tool.assert_called_once_with(
            "test_tool", {"param1": "value1"}
        )
        self.assertEqual(result["role"], "tool")
        self.assertEqual(result["tool_call_id"], "test-tool-call-id")
        self.assertEqual(result["content"], "Test result")

    @pytest.mark.asyncio
    @patch("json.loads")
    async def test_exec_tool_call_json_decode_error(self, mock_json_loads):
        agent = Agent(conf=self.mock_config)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "test-tool-call-id"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = "invalid json"

        mock_json_loads.side_effect = json.JSONDecodeError(
            "Invalid JSON", "invalid json", 0
        )

        with self.assertRaises(ToolCallError) as context:
            await agent.exec_tool_call(mock_tool_call)

        error_result = context.exception.tool_message
        self.assertEqual(error_result["role"], "tool")
        self.assertEqual(error_result["tool_call_id"], "test-tool-call-id")
        self.assertIn("Invalid JSON", error_result["content"])

    @pytest.mark.asyncio
    async def test_exec_tool_call_tool_not_found(self):
        agent = Agent(conf=self.mock_config)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "test-tool-call-id"
        mock_tool_call.function.name = "nonexistent_tool"
        mock_tool_call.function.arguments = '{"param1": "value1"}'

        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "different_tool"

        mock_server = MagicMock(spec=Server)
        agent.tools = [(mock_tool, mock_server)]

        with self.assertRaises(ToolCallError) as context:
            await agent.exec_tool_call(mock_tool_call)

        error_result = context.exception.tool_message
        self.assertEqual(error_result["role"], "tool")
        self.assertEqual(error_result["tool_call_id"], "test-tool-call-id")
        self.assertEqual(error_result["content"], "Tool not found.")

    @pytest.mark.asyncio
    async def test_exec_tool_call_execution_error(self):
        agent = Agent(conf=self.mock_config)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "test-tool-call-id"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"param1": "value1"}'

        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "test_tool"

        mock_server = MagicMock(spec=Server)
        mock_server.execute_tool = MagicMock(return_value=asyncio.Future())
        mock_server.execute_tool.return_value.set_exception(
            Exception("Tool execution failed")
        )

        agent.tools = [(mock_tool, mock_server)]

        with self.assertRaises(ToolCallError) as context:
            await agent.exec_tool_call(mock_tool_call)

        error_result = context.exception.tool_message
        self.assertEqual(error_result["role"], "tool")
        self.assertEqual(error_result["tool_call_id"], "test-tool-call-id")
        self.assertEqual(error_result["content"], "Tool execution failed")

    @pytest.mark.asyncio
    async def test_exec_tool_call_with_error_result(self):
        agent = Agent(conf=self.mock_config)

        mock_tool_call = MagicMock()
        mock_tool_call.id = "test-tool-call-id"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"param1": "value1"}'

        mock_tool = MagicMock(spec=Tool)
        mock_tool.name = "test_tool"

        mock_server = MagicMock(spec=Server)

        mock_result = MagicMock()
        mock_result.isError = True
        mock_result.content = [
            TextContent(
                type="text", text="Error: Tool execution failed", annotations=None
            )
        ]

        mock_server.execute_tool = MagicMock(return_value=asyncio.Future())
        mock_server.execute_tool.return_value.set_result(mock_result)

        agent.tools = [(mock_tool, mock_server)]

        with self.assertRaises(ToolCallError) as context:
            await agent.exec_tool_call(mock_tool_call)

        error_result = context.exception.tool_message
        self.assertEqual(error_result["role"], "tool")
        self.assertEqual(error_result["tool_call_id"], "test-tool-call-id")
        self.assertEqual(error_result["content"], "Error: Tool execution failed")

    @pytest.mark.asyncio
    @patch("opencodr.agent.console.print")
    async def test_check_circuit_breakers_all_fine(self, mock_print):
        agent = Agent(conf=self.mock_config)
        agent.curr_depth = 1
        agent.curr_tokens = 100
        self.mock_config.OC_MAX_DEPTH = 5
        self.mock_config.OC_MAX_TOKENS = 1000

        result = agent.check_circuit_breakers()

        self.assertTrue(result)
        mock_print.assert_not_called()

    @pytest.mark.asyncio
    @patch("opencodr.agent.console.print")
    @patch.object(Agent, "check_circuit_breakers", return_value=False)
    @patch.object(Agent, "handle_user_input")
    @patch.object(Agent, "handle_stream_completion")
    async def test_generate_with_circuit_breaker_triggered(
        self, mock_handle_stream, mock_handle_input, mock_check, mock_print
    ):
        agent = Agent(conf=self.mock_config)

        result = await agent.generate()

        mock_check.assert_called_once()
        mock_handle_input.assert_not_called()
        mock_handle_stream.assert_not_called()
        assert result is None

    @pytest.mark.asyncio
    @patch("opencodr.agent.Agent.check_circuit_breakers")
    @patch("opencodr.agent.Agent.handle_stream_completion", new_callable=AsyncMock)
    @patch("builtins.input", side_effect=["quit", "EOF"])
    async def test_generate_with_prompt(
        self, mock_input, mock_handle_stream, mock_check
    ):
        agent = Agent(conf=self.mock_config)
        test_prompt = "Test prompt"

        mock_response = ModelResponse(
            id="test_id",
            choices=[
                Choices(
                    message={"content": "Mocked response from OpenAI", "tool_calls": []}
                )
            ],
            created=1234567890,
            model="gpt-4",
            object="chat.completion",
        )

        mock_handle_stream.return_value = mock_response

        await agent.generate(prompt=test_prompt)

        assert mock_check.call_count == 2
        mock_handle_stream.assert_awaited_once()
        assert len(agent.messages) == 2
        assert agent.messages[1].role == "user"
        assert agent.messages[1].content == "Test prompt"
        assert mock_input.call_count == 2

    @pytest.mark.asyncio
    @patch("opencodr.agent.Agent.check_circuit_breakers")
    @patch("opencodr.agent.Agent.handle_stream_completion", new_callable=AsyncMock)
    @patch("builtins.input", side_effect=["Test prompt", "EOF", "quit", "EOF"])
    async def test_generate_with_user_input(
        self, mock_input, mock_handle_stream, mock_check
    ):
        agent = Agent(conf=self.mock_config)

        mock_response = ModelResponse(
            id="test_id",
            choices=[
                Choices(
                    message={"content": "Mocked response from OpenAI", "tool_calls": []}
                )
            ],
            created=1234567890,
            model="gpt-4",
            object="chat.completion",
        )

        mock_handle_stream.return_value = mock_response

        await agent.generate(prompt=None)

        assert mock_check.call_count == 2

        mock_handle_stream.assert_awaited_once()

        assert len(agent.messages) == 2
        assert agent.messages[1].role == "user"
        assert agent.messages[1].content == "Test prompt"
        assert mock_input.call_count == 4

    @patch("opencodr.agent.multiline_prompt", return_value="Hello, Agent!")
    async def test_handle_user_input_normal(self, mock_prompt):
        agent = Agent(conf=OpenCoderConfig(OC_MODEL="openai/gpt-4o"))
        result = await agent.handle_user_input()
        self.assertEqual(result, "Hello, Agent!")
        mock_prompt.assert_called()

    @patch("opencodr.agent.multiline_prompt", return_value="quit")
    @patch("sys.stdout.write")
    async def test_handle_user_input_quit(self, mock_stdout, mock_prompt):
        agent = Agent(conf=OpenCoderConfig(OC_MODEL="openai/gpt-4o"))
        result = await agent.handle_user_input()
        self.assertIsNone(result)
        mock_stdout.assert_called()
        mock_prompt.assert_called()

    @patch("opencodr.agent.multiline_prompt", return_value="e-2")
    @patch("opencodr.agent.Agent.handle_rewind", new_callable=AsyncMock)
    async def test_handle_user_input_rewind_edit(self, mock_rewind, mock_prompt):
        agent = Agent(conf=OpenCoderConfig(OC_MODEL="openai/gpt-4o"))
        result = await agent.handle_user_input()
        self.assertIsNone(result)
        mock_rewind.assert_awaited_once_with(2, edit=True)
        mock_prompt.assert_called()

    @patch("opencodr.agent.multiline_prompt", return_value="-1")
    @patch("opencodr.agent.Agent.handle_rewind", new_callable=AsyncMock)
    async def test_handle_user_input_rewind_no_edit(self, mock_rewind, mock_prompt):
        agent = Agent(conf=OpenCoderConfig(OC_MODEL="openai/gpt-4o"))
        result = await agent.handle_user_input()
        self.assertEqual(result, None)
        mock_rewind.assert_awaited_once_with(1, edit=False)
        mock_prompt.assert_called()

    @patch("opencodr.agent.multiline_prompt", return_value="")
    async def test_handle_user_input_empty(self, mock_prompt):
        agent = Agent(conf=OpenCoderConfig(OC_MODEL="openai/gpt-4o"))
        result = await agent.handle_user_input()
        self.assertEqual(result, "")
        mock_prompt.assert_called()

    @pytest.mark.asyncio
    @patch("builtins.input", side_effect=["quit", "EOF"])
    async def test_rewind_without_edit(self, mock_input):
        conf = OpenCoderConfig(OC_MODEL="gpt-4", OC_MAX_DEPTH=5, OC_MAX_TOKENS=5000)
        agent = Agent(
            conf=conf,
            messages=[
                Message(role="system", content="System message."),
                Message(role="user", content="User message 1"),
                Message(role="assistant", content="Assistant response 1"),
                Message(role="user", content="User message 2"),
                Message(role="assistant", content="Assistant response 2"),
            ],
        )

        await agent.handle_rewind(2, edit=False)

        assert len(agent.messages) == 3
        assert agent.messages[-1].role == "assistant"
        assert agent.messages[-1].content == "Assistant response 1"
        assert mock_input.call_count == 2

    @pytest.mark.asyncio
    @patch("opencodr.agent.edit_msg", side_effect=lambda text: "Edited " + text)
    @patch("builtins.input", side_effect=["quit", "EOF"])
    @patch("opencodr.agent.Agent.handle_stream_completion", new_callable=AsyncMock)
    async def test_rewind_with_edit(
        self,
        mock_handle_stream,
        mock_input,
        mock_edit_msg,
    ):
        conf = OpenCoderConfig(OC_MODEL="gpt-4")
        agent = Agent(
            conf=conf,
            messages=[
                Message(role="system", content="System message."),
                Message(role="user", content="User message 1"),
                Message(role="assistant", content="Assistant response 1"),
                Message(role="user", content="User message 2"),
            ],
        )

        mock_response = ModelResponse(
            id="test_id",
            choices=[
                Choices(
                    message={"content": "Mocked response from OpenAI", "tool_calls": []}
                )
            ],
            created=1234567890,
            model="gpt-4",
            object="chat.completion",
        )

        mock_handle_stream.return_value = mock_response

        await agent.handle_rewind(1, edit=True)
        assert mock_edit_msg.call_count == 1
        assert agent.messages[-1].content == "Edited User message 2"
        assert mock_input.call_count == 2


if __name__ == "__main__":
    unittest.main()
