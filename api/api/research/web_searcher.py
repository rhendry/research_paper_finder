import abc
from typing import AsyncIterator

from api.config import GOOGLE_SEARCH_PAUSE_SECONDS
from googlesearch import search


class WebSearcher(abc.ABC):
    @abc.abstractmethod
    async def top_urls_async(self, query: str, n: int = 10) -> AsyncIterator[str]:
        pass


class GoogleWebSearcher(WebSearcher):
    def __init__(self):
        self.pause = GOOGLE_SEARCH_PAUSE_SECONDS

    async def top_urls_async(self, query: str, n: int = 10) -> AsyncIterator[str]:
        print("Searching google for: ", query)
        for url in search(
            query,
            num=n,
            stop=n,
            pause=self.pause,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        ):
            yield url
