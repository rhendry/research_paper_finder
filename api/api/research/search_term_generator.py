import abc
from typing import AsyncIterator

from api.llm.openai_client import OpenAIClientWrapper, OpenAIModel, OpenAIParams
from api.llm.prompt_builder import PromptBuilder
from api.llm.streams import LineByLineStreamParser


class SearchTermGenerator(abc.ABC):
    @abc.abstractmethod
    async def generate_search_terms_async(
        self, user_topic: str, n: int = 10
    ) -> AsyncIterator[str]:
        pass


class OpenAIPDFSearchTermGenerator(SearchTermGenerator):
    def __init__(
        self,
        openai_client: OpenAIClientWrapper,
        stream_parser: LineByLineStreamParser,
    ):
        self.openai_client = openai_client
        self.stream_parser = stream_parser

    async def generate_search_terms_async(
        self, user_topic: str, n: int = 10
    ) -> AsyncIterator[str]:
        print("Generating search terms...")
        response_iterator = self.openai_client.stream_completion_async(
            model=OpenAIModel.GPT_3_5_TURBO_0125,
            prompt=PromptBuilder.system(
                f"""
                You are an academic researcher. You are an expert in generating Google search terms for scientific papers.
                Whenever a user provides you with a topic, simply generate search terms.

                Instructions:
                * Write one search term per line
                * You must not include any special characters in the search terms
                * You must not include anything other than search terms in your response
                * You must generate exactly {n} search terms
                * Vary the search terms to cover a wide range of topics related to the user's input

                Example:
                User topic: "I'm interested in quantum computing and cryptography"

                Example response:
                quantum computing and cryptography papers
                recent quantum computing papers
                recent cryptography papers
                """
            )
            .user(f"User topic: {user_topic}")
            .build(),
            params=OpenAIParams(max_tokens=100, temperature=0.8, top_p=0.9),
        )

        index = 0
        async for response in self.stream_parser.parse_stream_async(response_iterator):
            print("Yielding search term: ", response)
            yield f"{response} filetype:pdf"
            index += 1
            if index >= n:
                return
