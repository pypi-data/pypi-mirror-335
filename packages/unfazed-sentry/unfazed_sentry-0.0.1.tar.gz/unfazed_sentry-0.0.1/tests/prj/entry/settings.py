UNFAZED_SETTINGS = {
    "MIDDLEWARE": [
        "tests.prj.middleware.BaseMiddleware",
        "unfazed_sentry.middleware.common.SentryMiddleware",
    ],
    "LIFESPAN": ["unfazed_sentry.lifespan.UnfazedSentryLifeSpan"],
    "ROOT_URLCONF": "entry.routes",
}

UNFAZED_SENTRY_SETTINGS = {
    "DSN": "https://public@sentry.example.com/1",
    "ENVIRONMENT": "test",
    "SAMPLE_RATE": 1.0,
    "CLIENT_CLASS": "unfazed_sentry.settings.UnfazedSentrySettings",
    "SCOPE_HANDLERS": ["tests.prj.handler.BaseHandler"],
}
