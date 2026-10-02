from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.client import DocCheapError, request


class DocCheapProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # GET /v1/usage answers every valid key, the public sandbox key
        # included, and spends no credit.
        try:
            request(credentials.get("api_key", ""), "GET", "/v1/usage")
        except DocCheapError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc
