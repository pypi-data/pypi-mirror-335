from unfazed.lifespan import BaseLifeSpan

from .base import agent


class UnfazedSentryLifeSpan(BaseLifeSpan):
    async def on_startup(self) -> None:
        agent.setup()
