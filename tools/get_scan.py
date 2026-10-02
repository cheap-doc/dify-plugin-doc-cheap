from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.client import DocCheapError, request, scan_path, simplify_scan


class GetScanTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            scan = request(self.runtime.credentials["api_key"], "GET", scan_path(tool_parameters.get("scan_id")))
        except DocCheapError as exc:
            raise ValueError(str(exc)) from exc
        simplify = tool_parameters.get("simplify")
        yield self.create_json_message(scan if simplify is False else simplify_scan(scan))
