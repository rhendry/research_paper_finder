import abc
from aiostream import stream
from typing import AsyncIterator
import uuid
from api.config import RESULTS_PER_SEARCH_TERM, SEARCH_TERMS_PER_RESEARCH
from api.research.paper_summary_generator import PaperSummary, PaperSummaryGenerator
from api.research.search_term_generator import SearchTermGenerator
from api.research.web_searcher import WebSearcher
from api.types import Research, Search


class Researcher(abc.ABC):
    @abc.abstractmethod
    async def research_async(self, prompt: str) -> AsyncIterator[Research]:
        pass


class GooglePDFResearcher(Researcher):
    def __init__(
        self,
        search_term_generator: SearchTermGenerator,
        web_searcher: WebSearcher,
        paper_summary_generator: PaperSummaryGenerator,
    ):
        self.search_term_generator = search_term_generator
        self.web_searcher = web_searcher
        self.paper_summary_generator = paper_summary_generator

    async def _research_search_term_async(
        self, research: Research, search: Search
    ) -> AsyncIterator[Research]:
        print("Querying search term: ", search.query)

        # First thing we do is yield the current state of the Research object
        # The arguments are passed by reference, so we just have to modify them
        # and then yield `research` to update the frontend
        yield research

        async def _read_paper(url: str) -> AsyncIterator[Research]:
            print("Reading paper: ", url)
            yield research

            # Try to read the paper and extract the relevant information
            try:
                paper_summary = await self.paper_summary_generator.read_paper_async(url)
            except Exception as e:
                print("Failed to read paper:", e)
                return

            # Add to the search results
            search.papers.append(PaperSummary.to_paper(paper_summary, url))

            # Yield the updated research object with the paper details
            yield research

        # Search the web using the search term
        # TBH, not sure if the google client streams in results, but it does
        # use an iterator interface so I'll assume it does stream and that we
        # should start "reading the paper" as soon as each search result is ready
        paper_stream = stream.flatmap(
            self.web_searcher.top_urls_async(search.query, n=RESULTS_PER_SEARCH_TERM),
            _read_paper,
        )

        # Yield results from stream as they come in
        async with paper_stream.stream() as streamer:
            # Assume we're always modifying references and yielding the `research` object
            async for research in streamer:
                yield research

    async def research_async(self, prompt: str) -> AsyncIterator[Research]:
        # Initialize research context
        research = Research(id=str(uuid.uuid4()), prompt=prompt, searches=[])
        yield research

        async def _handle_search_term(search_term: str) -> AsyncIterator[Research]:
            # Kick-off a search-term-processing stream for each search term generated
            # This starts _immediately_ after the search term is streamed from the LLM.
            search = Search(query=search_term, papers=[])
            research.searches.append(search)
            yield research

            async for search in self._research_search_term_async(research, search):
                yield search

        # Generate search terms
        search_stream = stream.flatmap(
            self.search_term_generator.generate_search_terms_async(
                prompt, n=SEARCH_TERMS_PER_RESEARCH
            ),
            _handle_search_term,
        )

        # Yield results from stream as they come in
        async with search_stream.stream() as streamer:
            async for research in streamer:
                yield research
