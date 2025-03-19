import typing as t

from sentry_sdk import Scope


class BaseHandler:
    def __call__(self, scope: Scope, **kwargs: t.Any) -> None:
        if "foo" in kwargs:
            scope.set_tag("foo", kwargs["foo"])
