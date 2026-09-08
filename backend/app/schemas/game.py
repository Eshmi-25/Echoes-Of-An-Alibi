from datetime import datetime

from pydantic import BaseModel, Field


class CaseSummary(BaseModel):
    id: int
    slug: str
    title: str


class CaseDetail(BaseModel):
    id: int
    slug: str
    title: str
    briefing: str
    max_actions: int


class InvestigationSummary(BaseModel):
    id: int
    case_id: int
    status: str
    actions_remaining: int
    created_at: datetime


class InvestigationDetail(BaseModel):
    id: int
    case_id: int
    status: str
    actions_remaining: int
    visited_locations: list[str]
    discussed_topics: list[str]


class StartInvestigationRequest(BaseModel):
    case_id: int


class LocationStateResponse(BaseModel):
    location_slug: str
    unlocked: bool
    searched_count: int


class LocationSearchResponse(BaseModel):
    actions_remaining: int
    found_clues: list[str]
    newly_unlocked_locations: list[str]
    newly_unlocked_suspects: list[str]


class SuspectStateResponse(BaseModel):
    suspect_slug: str
    unlocked: bool
    trust: int
    pressure: int
    interviewed_count: int


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    topic_slug: str | None = None
    evidence_clue_slug: str | None = None


class ConfrontRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    clue_slug: str


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
    emotion: str = "calm"
    contradiction_exposed: bool = False
    unlocked_topics: list[str] = []
    ai_debug: dict | None = None


class ClueResponse(BaseModel):
    clue_slug: str
    title: str
    description: str
    location_slug: str
    tags: list[str]


class ContradictionResponse(BaseModel):
    slug: str
    title: str
    description: str


class NoteCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=3000)


class NotePatchRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    body: str | None = Field(default=None, min_length=1, max_length=3000)


class NoteResponse(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime


class BoardNodePayload(BaseModel):
    id: str
    type: str
    label: str
    x: int
    y: int
    extra: dict = {}


class BoardEdgePayload(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""


class BoardPayload(BaseModel):
    nodes: list[BoardNodePayload]
    edges: list[BoardEdgePayload]


class AccusationRequest(BaseModel):
    attacker_slug: str
    thief_slug: str
    motive: str
    supporting_clues: list[str] = Field(min_length=2)
    explanation: str = Field(min_length=10, max_length=2000)


class ResultResponse(BaseModel):
    score: int
    ending_slug: str
    ending_title: str
    ending_summary: str
    canonical_revealed: bool


class HealthResponse(BaseModel):
    status: str


class AIStatusResponse(BaseModel):
    enabled: bool
    provider: str
    model: str
