from typing import Any, Literal

from strix.tools.registry import register_tool

from .burp_proxy_manager import get_burp_proxy_manager


RequestPart = Literal["request", "response"]


@register_tool
def list_requests(
    httpql_filter: str | None = None,
    start_page: int = 1,
    end_page: int = 1,
    page_size: int = 50,
    sort_by: Literal[
        "timestamp",
        "host",
        "method",
        "path",
        "status_code",
        "response_time",
        "response_size",
        "source",
    ] = "timestamp",
    sort_order: Literal["asc", "desc"] = "desc",
    scope_id: str | None = None,
) -> dict[str, Any]:
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    return asyncio.run(manager.get_captured_requests(limit=page_size))


@register_tool
def view_request(
    request_id: str,
    part: RequestPart = "request",
    search_pattern: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict[str, Any]:
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    return asyncio.run(manager.get_request_details(request_id))


@register_tool
def send_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: str = "",
    timeout: int = 30,
) -> dict[str, Any]:
    if headers is None:
        headers = {}
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    return asyncio.run(manager.send_request(method, url, headers, body))


@register_tool
def repeat_request(
    request_id: str,
    modifications: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if modifications is None:
        modifications = {}
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    # For now, return a placeholder - this would need to be implemented
    # based on the specific BurpSuite Pro API capabilities
    return {"status": "not_implemented", "message": "Repeat request not yet implemented for BurpSuite Pro"}


@register_tool
def scope_rules(
    action: Literal["get", "list", "create", "update", "delete"],
    allowlist: list[str] | None = None,
    denylist: list[str] | None = None,
    scope_id: str | None = None,
    scope_name: str | None = None,
) -> dict[str, Any]:
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    
    if action == "get":
        return asyncio.run(manager.get_scope())
    elif action == "create" and allowlist:
        return asyncio.run(manager.add_to_scope(allowlist))
    elif action == "delete" and denylist:
        return asyncio.run(manager.remove_from_scope(denylist))
    else:
        return {"status": "not_implemented", "message": f"Action {action} not yet implemented for BurpSuite Pro"}


@register_tool
def list_sitemap(
    scope_id: str | None = None,
    parent_id: str | None = None,
    depth: Literal["DIRECT", "ALL"] = "DIRECT",
    page: int = 1,
) -> dict[str, Any]:
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    return asyncio.run(manager.get_target_info())


@register_tool
def view_sitemap_entry(
    entry_id: str,
) -> dict[str, Any]:
    import asyncio
    manager = asyncio.run(get_burp_proxy_manager())
    return asyncio.run(manager.get_request_details(entry_id))
