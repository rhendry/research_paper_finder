import os
import dotenv

dotenv.load_dotenv()

SEARCH_TERMS_PER_RESEARCH = float(os.getenv("SEARCH_TERMS_PER_RESEARCH", 3))
RESULTS_PER_SEARCH_TERM = float(os.getenv("RESULTS_PER_SEARCH_TERM", 10))
GOOGLE_SEARCH_PAUSE_SECONDS = float(os.getenv("GOOGLE_SEARCH_PAUSE_SECONDS", 4))

OPENAI_PAPER_TEXT_CONTEXT_LENGTH = float(
    os.getenv("OPENAI_PAPER_TEXT_CONTEXT_LENGTH", 5000)
)
OPENAI_DEFAULT_MAX_TOKENS = int(os.getenv("OPENAI_DEFAULT_MAX_TOKENS", 4000))
OPENAI_DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.1))
OPENAI_DEFAULT_TOP_P = float(os.getenv("OPENAI_TOP_P", 0.8))

PAPER_DOWNLOAD_TIMEOUT_SECONDS = float(os.getenv("PAPER_DOWNLOAD_TIMEOUT", 30))


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "No API key provided for OpenAI. Please set the OPEN_API_KEY environment variable in your .env file."
    )
