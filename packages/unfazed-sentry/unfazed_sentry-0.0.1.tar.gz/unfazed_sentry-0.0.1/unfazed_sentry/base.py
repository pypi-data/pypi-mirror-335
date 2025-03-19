import typing as t

import sentry_sdk
from unfazed.conf import settings
from unfazed.utils import import_string

from .settings import UnfazedSentrySettings


class UnfazedSentry:
    scope_handlers: t.List[t.Callable[[sentry_sdk.Scope], None]] = []

    def setup(self) -> None:
        sentry_settings: UnfazedSentrySettings = settings["UNFAZED_SENTRY_SETTINGS"]
        sentry_sdk.init(
            dsn=sentry_settings.dsn,
            environment=sentry_settings.environment,
            debug=sentry_settings.debug,
            sample_rate=sentry_settings.sample_rate,
            ignore_errors=sentry_settings.ignore_errors,
            server_name=sentry_settings.server_name,
        )
        handlers = [
            import_string(handler)() for handler in sentry_settings.scope_handlers
        ]
        self.scope_handlers = handlers

    def capture_exception(self, exception: Exception, **kwargs: t.Any) -> None:
        if hasattr(exception, "should_capture") and not exception.should_capture:
            return

        # TODO
        # push_scope is deprecated in next version
        with sentry_sdk.push_scope() as scope:
            for handler in self.scope_handlers:
                handler(scope, **kwargs)
            sentry_sdk.capture_exception(exception)


agent: UnfazedSentry = UnfazedSentry()
