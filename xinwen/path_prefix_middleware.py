"""网关以 /xinwen 等为前缀转发且未剥离路径时，把 scope['path'] 还原为应用内路径。"""
from __future__ import annotations


class PrefixStripMiddleware:
    def __init__(self, app, prefix: str):
        self.app = app
        self.prefix = prefix.rstrip("/")

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path") or ""
            p = self.prefix
            if path == p or path.startswith(p + "/"):
                scope = dict(scope)
                scope["path"] = path[len(p) :] or "/"
        await self.app(scope, receive, send)
