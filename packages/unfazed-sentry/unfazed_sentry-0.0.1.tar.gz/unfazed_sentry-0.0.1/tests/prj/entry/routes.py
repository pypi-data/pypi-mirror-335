import typing as t

from unfazed.exception import ParameterError
from unfazed.http import HttpRequest, HttpResponse
from unfazed.route import Route, path

from unfazed_sentry import capture_exception


async def index(request: HttpRequest) -> HttpResponse:
    raise ParameterError("test")


async def not_capture(request: HttpRequest) -> HttpResponse:
    err = ParameterError("test")
    err.should_capture = False

    raise err


async def with_scope(request: HttpRequest) -> HttpResponse:
    capture_exception(ParameterError("test"), foo="bar")
    return HttpResponse("ok")


patterns: t.List[Route] = [
    path("/", endpoint=index),
    path("/not-capture", endpoint=not_capture),
    path("/with-scope", endpoint=with_scope),
]
