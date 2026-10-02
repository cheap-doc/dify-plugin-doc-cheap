from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.client import DocCheapError, request


class GetUsageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            usage = request(self.runtime.credentials["api_key"], "GET", "/v1/usage")
        except DocCheapError as exc:
            raise ValueError(str(exc)) from exc
        yield self.create_json_message(usage)
