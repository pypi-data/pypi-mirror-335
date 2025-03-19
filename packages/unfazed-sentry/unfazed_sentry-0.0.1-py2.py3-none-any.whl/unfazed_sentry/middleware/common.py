from starlette.types import ASGIApp, Receive, Scope, Send

from unfazed_sentry import capture_exception


class SentryMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            capture_exception(e)
            raise e
