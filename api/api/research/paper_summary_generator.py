import abc
from typing import List

from api.config import OPENAI_PAPER_TEXT_CONTEXT_LENGTH
from api.llm.openai_client import OpenAIClientWrapper, OpenAIModel
from api.llm.prompt_builder import PromptBuilder
from api.llm.yaml_parser import parse_yaml_object
from api.research.paper_text_extractor import PaperTextExtractor
from api.types import Paper
from pydantic import BaseModel, Field


class PaperSummary(BaseModel):
    title: str = Field(description="The title of the paper")
    summary: str = Field(description="A brief summary of the paper")
    authors: List[str] | None = Field(
        description="The authors of the paper", default=None
    )
    publisher: str | None = Field(
        description="The journal or other venue where the paper was published",
        default=None,
    )

    @classmethod
    def to_paper(cls, paper_summary: "PaperSummary", url: str) -> Paper:
        return Paper(
            title=paper_summary.title,
            summary=paper_summary.summary,
            url=url,
            authors=paper_summary.authors,
            publisher=paper_summary.publisher,
        )


class PaperSummaryGenerator(abc.ABC):
    async def read_paper_async(self, url: str) -> PaperSummary:
        pass


class OpenAIPaperSummaryGenerator(PaperSummaryGenerator):
    def __init__(
        self,
        paper_text_extractor: PaperTextExtractor,
        openai_client: OpenAIClientWrapper,
    ):
        self.paper_text_extractor = paper_text_extractor
        self.openai_client = openai_client

    async def read_paper_async(self, url: str) -> PaperSummary:
        # Get the text
        text = await self.paper_text_extractor.extract_paper_text_async(
            url, OPENAI_PAPER_TEXT_CONTEXT_LENGTH
        )

        # Build prompt
        prompt = (
            PromptBuilder.system(
                """
You are an academic researcher. You are an expert in reading scientific papers and summarizing them,
so that other researchers can quickly understand their chief claims, discoveries, and conclusions.
"""
            )
            .user(
                """
Paper text: 
{text}

Instructions:
* Read the text carefully. It may be truncated or missing sections, but it's important to understand the main points.
* Focus on the context (specific field of research, problem addressed), methodology (how the research was conducted), and conclusions (the main findings and their implications).

Response format:
Given the paper text, write a YAML object equivalent to type $Paper, according to the Pydantic definitons below. 
Do NOT use any markdown or additional text in the output other than the YAML object (DO NOT START WITH ```yaml, just write the pure yaml). 
Use block style for all strings to avoid escaping characters.

class PaperSummary(BaseModel):
    title: str = Field(description="The title of the paper")
    summary: str = Field(description="A brief summary of the paper")
    authors: List[str] | None = Field(description="The authors of the paper", default=None)
    publisher: str | None = Field(description="The journal or other venue where the paper was published", default=None)


Example response:
title: |
    The title of the paper
summary: |
    A summary of the paper with the context, methodology, and conclusions.
authors: 
    - Author 1
    - Author 2
publisher: |
    Cornell University Press
date: 2022-01-01
doi: 10.1234/5678
tags: 
    - science
    - technology
    - other tag


Your response:
""".format(text=text)
            )
            .build()
        )

        # Generate summary of the paper
        response = await self.openai_client.get_completion_async(
            OpenAIModel.GPT_3_5_TURBO_0125, prompt
        )

        # Parse the response
        return parse_yaml_object(response, PaperSummary)
