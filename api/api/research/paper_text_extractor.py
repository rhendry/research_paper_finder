import abc
import tempfile

from api.config import PAPER_DOWNLOAD_TIMEOUT_SECONDS
from pypdf import PdfReader
import httpx


class PaperTextExtractor(abc.ABC):
    @abc.abstractmethod
    async def extract_paper_text_async(self, url: str, max_chars: int = -1) -> str:
        pass


class PDFPaperTextExtractor(PaperTextExtractor):
    async def extract_paper_text_async(self, url: str, max_chars: int = -1) -> str:
        # Download the paper
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, follow_redirects=True, timeout=PAPER_DOWNLOAD_TIMEOUT_SECONDS
            )

        # Write to a temporary file
        temp_pdf = tempfile.TemporaryFile()
        temp_pdf.write(response.content)

        total_chars = 0
        try:
            # Copy to temporyt file
            temp_pdf.write(response.content)
            temp_pdf.seek(0)

            # Extract text from PDF
            reader = PdfReader(temp_pdf)
            pages = []
            for page in reader.pages:
                page_text = page.extract_text()

                chars_to_go = int(max_chars - total_chars)
                total_chars += len(page_text)

                if max_chars > 0 and total_chars > max_chars:
                    pages.append(page_text[:chars_to_go])
                    break

                pages.append(page_text)

        finally:
            temp_pdf.close()

        return "\n".join(pages)
