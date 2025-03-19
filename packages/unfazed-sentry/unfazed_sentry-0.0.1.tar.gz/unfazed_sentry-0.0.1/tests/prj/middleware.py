from starlette.types import ASGIApp, Receive, Scope, Send
from unfazed.http import HttpResponse


class BaseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            ret = str(e)
            await HttpResponse(ret)(scope, receive, send)
