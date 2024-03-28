from api.config import OPENAI_API_KEY
from api.llm.openai_client import DefaultOpenAIClientWrapper
from api.llm.streams import DefaultLineByLineStreamParser
from api.research.paper_summary_generator import OpenAIPaperSummaryGenerator
from api.research.paper_text_extractor import (
    PDFPaperTextExtractor,
)
from api.research.researcher import GooglePDFResearcher
from api.research.search_term_generator import OpenAIPDFSearchTermGenerator
from api.research.web_searcher import GoogleWebSearcher
from openai import AsyncOpenAI


def get_researcher():
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    openai_client_wrapper = DefaultOpenAIClientWrapper(openai_client)
    stream_parser = DefaultLineByLineStreamParser()
    search_term_generator = OpenAIPDFSearchTermGenerator(
        openai_client_wrapper, stream_parser
    )
    web_searcher = GoogleWebSearcher()
    paper_text_extractor = PDFPaperTextExtractor()
    paper_summary_generator = OpenAIPaperSummaryGenerator(
        paper_text_extractor, openai_client_wrapper
    )
    return GooglePDFResearcher(
        search_term_generator, web_searcher, paper_summary_generator
    )
