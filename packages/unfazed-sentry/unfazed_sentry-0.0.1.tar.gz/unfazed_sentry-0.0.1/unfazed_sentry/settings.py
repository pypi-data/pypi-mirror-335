import typing as t

from pydantic import BaseModel, Field


class UnfazedSentrySettings(BaseModel):
    scope_handlers: t.List[str] = Field(
        [], description="The scope handlers", alias="SCOPE_HANDLERS"
    )
    dsn: str = Field(..., description="The DSN of the Sentry instance", alias="DSN")
    max_breadcrumbs: int = Field(
        2,
        description="The maximum number of breadcrumbs to store",
        alias="MAX_BREADCRUMBS",
    )
    debug: bool = Field(
        False, description="Whether to enable debug mode", alias="DEBUG"
    )
    environment: str = Field(
        "production",
        description="The environment of the Sentry instance",
        alias="ENVIRONMENT",
    )
    sample_rate: float = Field(
        1.0, description="The sample rate of the Sentry instance", alias="SAMPLE_RATE"
    )
    ignore_errors: t.Sequence[str | type] = Field(
        [], description="The errors to ignore", alias="IGNORE_ERRORS"
    )
    server_name: t.Optional[str] = Field(
        None, description="The name of the server", alias="SERVER_NAME"
    )
