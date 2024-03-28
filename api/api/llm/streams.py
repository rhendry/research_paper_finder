import abc
from typing import AsyncIterator


class LineByLineStreamParser(abc.ABC):
    @abc.abstractmethod
    async def parse_stream_async(
        self, iterator: AsyncIterator[str]
    ) -> AsyncIterator[str]:
        pass


class DefaultLineByLineStreamParser(LineByLineStreamParser):
    async def parse_stream_async(
        self, iterator: AsyncIterator[str]
    ) -> AsyncIterator[str]:
        buffer = ""

        async for chunk in iterator:
            if chunk is None:
                continue

            buffer += chunk

            # Attempt to parse complete JSON objects
            while buffer:
                obj, obj_ended, remainder = buffer.partition("\n")

                if obj_ended:
                    buffer = remainder  # Keep the remaining part in the buffer
                    yield obj
                else:
                    # Object end not found, keep the current buffer and wait for more chunks
                    break
