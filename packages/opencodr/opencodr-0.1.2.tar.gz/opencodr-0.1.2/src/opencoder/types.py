from openai.types.chat import ChatCompletionToolMessageParam


class ToolCallError(Exception):
    def __init__(self, tool_message: ChatCompletionToolMessageParam):
        self.tool_message = tool_message
        super().__init__(str(tool_message["content"]))
