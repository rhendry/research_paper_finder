from typing import Annotated, AsyncIterator
from api.deps import get_researcher
from api.research.researcher import Researcher
from api.types import ResearchSnapshot
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

END_STREAM_SENTINAL = "<<HALT>>"


async def generate_messages(
    user_prompt: str, researcher: Researcher
) -> AsyncIterator[ResearchSnapshot]:
    index = 0
    async for research_update in researcher.research_async(user_prompt):
        yield ResearchSnapshot(order=index, research=research_update).model_dump_json()
        index += 1

    yield END_STREAM_SENTINAL


@router.get(
    "/research/create",
    summary="Endpoint for receiving a user prompt and returning server-sent events",
    response_model=ResearchSnapshot,  # Enables generating typescript types from OpenAPI schema
)
async def research_create(
    researcher: Annotated[Researcher, Depends(get_researcher)], prompt: str
) -> EventSourceResponse:
    event_generator = generate_messages(prompt, researcher)
    return EventSourceResponse(event_generator)


@router.get("/")
async def default():
    return {"message": "Hello World"}
