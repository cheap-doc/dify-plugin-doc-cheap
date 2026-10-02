from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.client import DocCheapError, build_scan_body, download_image, request, simplify_scan


class RecognizeDocumentTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        file = tool_parameters.get("image")
        image_url = str(tool_parameters.get("image_url") or "").strip()
        try:
            if file is not None:
                image = file.blob
            elif image_url:
                image = download_image(image_url)
            else:
                raise DocCheapError("Give an image file or an image URL.")
            body = build_scan_body(
                image,
                expect_country=tool_parameters.get("expect_country"),
                return_portrait=tool_parameters.get("return_portrait"),
                retain_hours=tool_parameters.get("retain_hours"),
                reference=tool_parameters.get("reference"),
            )
            headers = {}
            idempotency_key = str(tool_parameters.get("idempotency_key") or "").strip()
            if idempotency_key:
                headers["Idempotency-Key"] = idempotency_key
            scan = request(self.runtime.credentials["api_key"], "POST", "/v1/scans", json_body=body, headers=headers)
        except DocCheapError as exc:
            raise ValueError(str(exc)) from exc
        simplify = tool_parameters.get("simplify")
        yield self.create_json_message(scan if simplify is False else simplify_scan(scan))
