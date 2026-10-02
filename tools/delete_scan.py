from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.client import DocCheapError, request, scan_path


class DeleteScanTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            path = scan_path(tool_parameters.get("scan_id"))
            result = request(self.runtime.credentials["api_key"], "DELETE", path)
        except DocCheapError as exc:
            raise ValueError(str(exc)) from exc
        yield self.create_json_message(result or {"id": str(tool_parameters.get("scan_id")).strip(), "deleted": True})
