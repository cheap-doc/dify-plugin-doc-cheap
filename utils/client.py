"""HTTP client for the doc.cheap API shared by the provider and every tool."""

from __future__ import annotations

import base64
import re
from typing import Any
from urllib.parse import quote, urlparse

import httpx

API_BASE_URL = "https://api.doc.cheap"
USER_AGENT = "doc-cheap-dify-plugin/0.0.1"
REQUEST_TIMEOUT = httpx.Timeout(60.0, connect=10.0)
DOWNLOAD_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
# The API caps a request body at 36 MiB; base64 adds a third, so the raw image
# must stay under 27 MiB to fit. 25 MiB leaves room for the JSON around it.
MAX_IMAGE_BYTES = 25 * 1024 * 1024
COUNTRY_CODE = re.compile(r"^[A-Z]{3}$")


class DocCheapError(Exception):
    """A failed call, worded for the person reading the workflow log."""


def _headers(api_key: str) -> dict[str, str]:
    key = (api_key or "").strip()
    if not key:
        raise DocCheapError("The doc.cheap API key is empty.")
    return {"Authorization": f"Bearer {key}", "User-Agent": USER_AGENT, "Accept": "application/json"}


def _raise_for_api_error(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        body = response.json()
    except ValueError:
        body = None
    error = body.get("error") if isinstance(body, dict) else None
    if isinstance(error, dict) and isinstance(error.get("code"), str) and isinstance(error.get("message"), str):
        parts = [error["message"], f"Error code: {error['code']}."]
        if isinstance(error.get("docs_url"), str):
            parts.append(f"What it means and what to do: {error['docs_url']}")
        if isinstance(error.get("request_id"), str):
            parts.append(f"Request ID: {error['request_id']}")
        raise DocCheapError(" ".join(parts))
    raise DocCheapError(f"The doc.cheap API answered with HTTP {response.status_code}.")


def request(api_key: str, method: str, path: str, json_body: Any = None, headers: dict[str, str] | None = None) -> Any:
    merged = _headers(api_key)
    if headers:
        merged.update(headers)
    try:
        response = httpx.request(
            method,
            f"{API_BASE_URL}{path}",
            json=json_body,
            headers=merged,
            timeout=REQUEST_TIMEOUT,
        )
    except httpx.HTTPError as exc:
        raise DocCheapError(f"Could not reach the doc.cheap API: {type(exc).__name__}.") from exc
    _raise_for_api_error(response)
    if response.status_code == 204 or not response.content:
        return None
    return response.json()


def scan_path(scan_id: Any) -> str:
    value = str(scan_id or "").strip()
    if not value:
        raise DocCheapError("Scan ID is empty. Pass the id that Recognize Document returned.")
    return f"/v1/scans/{quote(value, safe='')}"


def download_image(url: str) -> bytes:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise DocCheapError("Image URL must be an http or https address.")
    try:
        with httpx.stream(
            "GET", parsed.geturl(), timeout=DOWNLOAD_TIMEOUT, follow_redirects=True, headers={"User-Agent": USER_AGENT}
        ) as response:
            if not response.is_success:
                raise DocCheapError(f"Could not download the image: HTTP {response.status_code}.")
            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > MAX_IMAGE_BYTES:
                    raise DocCheapError("The image is larger than 25 MiB.")
                chunks.append(chunk)
    except httpx.HTTPError as exc:
        raise DocCheapError(f"Could not download the image: {type(exc).__name__}.") from exc
    return b"".join(chunks)


def build_scan_body(
    image: bytes,
    expect_country: Any = None,
    return_portrait: Any = None,
    retain_hours: Any = None,
    reference: Any = None,
) -> dict[str, Any]:
    if not image:
        raise DocCheapError("The image is empty.")
    if len(image) > MAX_IMAGE_BYTES:
        raise DocCheapError("The image is larger than 25 MiB.")
    options: dict[str, Any] = {}
    country = str(expect_country or "").strip().upper()
    if country:
        if not COUNTRY_CODE.match(country):
            raise DocCheapError("Expected Country must be a three-letter code such as GRC.")
        options["expect_country"] = country
    if isinstance(return_portrait, bool):
        options["return_portrait"] = return_portrait
    if retain_hours is not None and retain_hours != "":
        try:
            hours = float(retain_hours)
        except (TypeError, ValueError) as exc:
            raise DocCheapError("Keep Result (Hours) must be a whole number from 0 to 8760.") from exc
        if not hours.is_integer() or not 0 <= hours <= 8760:
            raise DocCheapError("Keep Result (Hours) must be a whole number from 0 to 8760.")
        options["retain_hours"] = int(hours)
    body: dict[str, Any] = {"image": base64.b64encode(image).decode("ascii")}
    if options:
        body["options"] = options
    ref = str(reference or "").strip()
    if ref:
        if len(ref) > 128:
            raise DocCheapError("Reference must be 128 characters or fewer.")
        body["reference"] = ref
    return body


def _section(scan: Any, key: str) -> dict[str, Any]:
    value = scan.get(key) if isinstance(scan, dict) else None
    return value if isinstance(value, dict) else {}


def simplify_scan(scan: Any) -> dict[str, Any]:
    """The flat view most workflows need: who, which document, can it be trusted."""
    meta = _section(scan, "meta")
    document = _section(scan, "document")
    holder = _section(scan, "holder")
    mrz = _section(scan, "mrz")
    return {
        "id": meta.get("id"),
        "status": meta.get("status"),
        "confidence": meta.get("confidence"),
        "billed": meta.get("billed"),
        "reference": meta.get("reference"),
        "document_kind": document.get("kind"),
        "document_country": document.get("country"),
        "document_number": document.get("number"),
        "expiry_date": document.get("expiry_date"),
        "is_expired": document.get("is_expired"),
        "surname": holder.get("surname"),
        "given_names": holder.get("given_names"),
        "birth_date": holder.get("birth_date"),
        "sex": holder.get("sex"),
        "nationality": holder.get("nationality"),
        "mrz_status": mrz.get("status"),
    }
