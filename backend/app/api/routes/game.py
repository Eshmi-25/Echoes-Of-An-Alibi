from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.exceptions import forbidden, not_found
from app.core.rate_limit import InMemoryRateLimiter
from app.db.models.models import (
    Accusation,
    BoardEdge,
    BoardNode,
    Case,
    Clue,
    Contradiction,
    ConversationMessage,
    DetectiveNote,
    DialogueTopic,
    Ending,
    Investigation,
    InvestigationClue,
    InvestigationLocationState,
    InvestigationSuspectState,
    Location,
    Suspect,
    User,
)
from app.db.session import get_db
from app.schemas.game import (
    AIStatusResponse,
    AccusationRequest,
    BoardPayload,
    CaseDetail,
    CaseSummary,
    ChatMessageRequest,
    ChatMessageResponse,
    ClueResponse,
    ConfrontRequest,
    ContradictionResponse,
    HealthResponse,
    InvestigationDetail,
    InvestigationSummary,
    LocationSearchResponse,
    LocationStateResponse,
    NoteCreateRequest,
    NotePatchRequest,
    NoteResponse,
    ResultResponse,
    StartInvestigationRequest,
    SuspectStateResponse,
)
from app.services.dialogue_service import DialogueService
from app.services.game_engine import GameEngine
from app.services.scoring_service import ScoringService

router = APIRouter(tags=["game"])
settings = get_settings()
rate_limiter = InMemoryRateLimiter(limit=settings.interview_rate_limit)
engine = GameEngine()
dialogue = DialogueService(settings)


def owned_investigation_or_404(db: Session, user: User, investigation_id: int) -> Investigation:
    inv = db.get(Investigation, investigation_id)
    if not inv:
        raise not_found("Investigation not found")
    if inv.user_id != user.id:
        raise forbidden()
    return inv


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")


@router.get("/ai/status", response_model=AIStatusResponse)
def ai_status():
    return AIStatusResponse(
        enabled=settings.ollama_enabled,
        provider="ollama+fallback",
        model=settings.ollama_model,
    )


@router.get("/cases", response_model=list[CaseSummary])
def list_cases(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Case).all()
    return [CaseSummary(id=c.id, slug=c.slug, title=c.title) for c in rows]


@router.get("/cases/{case_id}", response_model=CaseDetail)
def get_case(case_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    case = db.get(Case, case_id)
    if not case:
        raise not_found("Case not found")
    return CaseDetail(
        id=case.id,
        slug=case.slug,
        title=case.title,
        briefing=case.briefing,
        max_actions=case.max_actions,
    )


@router.post("/investigations", response_model=InvestigationSummary, status_code=status.HTTP_201_CREATED)
def start_investigation(
    payload: StartInvestigationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = db.get(Case, payload.case_id)
    if not case:
        raise not_found("Case not found")

    inv = Investigation(user_id=user.id, case_id=case.id, actions_remaining=case.max_actions)
    db.add(inv)
    db.flush()

    for loc in db.query(Location).filter_by(case_id=case.id).all():
        unlocked = loc.unlock_rule is None
        db.add(
            InvestigationLocationState(
                investigation_id=inv.id,
                location_slug=loc.slug,
                unlocked=unlocked,
            )
        )

    for sus in db.query(Suspect).filter_by(case_id=case.id).all():
        db.add(
            InvestigationSuspectState(
                investigation_id=inv.id,
                suspect_slug=sus.slug,
                unlocked=(sus.slug in ["marina-crowe", "jonah-pryce"]),
            )
        )

    db.commit()
    db.refresh(inv)
    return InvestigationSummary(
        id=inv.id,
        case_id=inv.case_id,
        status=inv.status,
        actions_remaining=inv.actions_remaining,
        created_at=inv.created_at,
    )


@router.get("/investigations", response_model=list[InvestigationSummary])
def list_investigations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Investigation).filter_by(user_id=user.id).order_by(Investigation.id.desc()).all()
    return [
        InvestigationSummary(
            id=i.id,
            case_id=i.case_id,
            status=i.status,
            actions_remaining=i.actions_remaining,
            created_at=i.created_at,
        )
        for i in rows
    ]


@router.get("/investigations/{investigation_id}", response_model=InvestigationDetail)
def get_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    return InvestigationDetail(
        id=inv.id,
        case_id=inv.case_id,
        status=inv.status,
        actions_remaining=inv.actions_remaining,
        visited_locations=inv.visited_locations,
        discussed_topics=inv.discussed_topics,
    )


@router.post("/investigations/{investigation_id}/restart", response_model=InvestigationSummary)
def restart_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    case = db.get(Case, inv.case_id)
    inv.actions_remaining = case.max_actions
    inv.status = "active"
    inv.visited_locations = []
    inv.discussed_topics = []
    inv.exposed_contradictions = []

    db.query(InvestigationClue).filter_by(investigation_id=inv.id).delete()
    db.query(ConversationMessage).filter_by(investigation_id=inv.id).delete()
    db.query(DetectiveNote).filter_by(investigation_id=inv.id).delete()
    db.query(BoardNode).filter_by(investigation_id=inv.id).delete()
    db.query(BoardEdge).filter_by(investigation_id=inv.id).delete()
    db.query(Accusation).filter_by(investigation_id=inv.id).delete()

    for ls in db.query(InvestigationLocationState).filter_by(investigation_id=inv.id).all():
        loc = db.query(Location).filter_by(case_id=inv.case_id, slug=ls.location_slug).one()
        ls.unlocked = loc.unlock_rule is None
        ls.searched_count = 0

    for ss in db.query(InvestigationSuspectState).filter_by(investigation_id=inv.id).all():
        ss.unlocked = ss.suspect_slug in ["marina-crowe", "jonah-pryce"]
        ss.trust = 50
        ss.pressure = 0
        ss.interviewed_count = 0

    db.commit()
    db.refresh(inv)
    return InvestigationSummary(
        id=inv.id,
        case_id=inv.case_id,
        status=inv.status,
        actions_remaining=inv.actions_remaining,
        created_at=inv.created_at,
    )


@router.get("/investigations/{investigation_id}/locations", response_model=list[LocationStateResponse])
def list_locations(investigation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    rows = db.query(InvestigationLocationState).filter_by(investigation_id=inv.id).all()
    return [
        LocationStateResponse(location_slug=r.location_slug, unlocked=r.unlocked, searched_count=r.searched_count)
        for r in rows
    ]


@router.get("/investigations/{investigation_id}/locations/{location_id}")
def get_location(
    investigation_id: int,
    location_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    state = db.query(InvestigationLocationState).filter_by(investigation_id=inv.id, location_slug=location_id).first()
    if not state:
        raise not_found("Location not found")
    loc = db.query(Location).filter_by(case_id=inv.case_id, slug=location_id).one()
    return {
        "slug": loc.slug,
        "name": loc.name,
        "description": loc.description,
        "unlocked": state.unlocked,
        "searched_count": state.searched_count,
    }


@router.post(
    "/investigations/{investigation_id}/locations/{location_id}/search",
    response_model=LocationSearchResponse,
)
def search_location(
    investigation_id: int,
    location_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    state = db.query(InvestigationLocationState).filter_by(investigation_id=inv.id, location_slug=location_id).first()
    if not state or not state.unlocked:
        raise HTTPException(status_code=403, detail="Location locked")

    before = inv.actions_remaining
    found, new_locations, new_suspects = engine.search_location(db, inv, location_id)
    if before <= 0:
        raise HTTPException(status_code=400, detail="No actions remaining")

    db.commit()
    db.refresh(inv)
    return LocationSearchResponse(
        actions_remaining=inv.actions_remaining,
        found_clues=found,
        newly_unlocked_locations=new_locations,
        newly_unlocked_suspects=new_suspects,
    )


@router.get("/investigations/{investigation_id}/suspects", response_model=list[SuspectStateResponse])
def list_suspects(investigation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    rows = db.query(InvestigationSuspectState).filter_by(investigation_id=inv.id).all()
    return [
        SuspectStateResponse(
            suspect_slug=r.suspect_slug,
            unlocked=r.unlocked,
            trust=r.trust,
            pressure=r.pressure,
            interviewed_count=r.interviewed_count,
        )
        for r in rows
    ]


@router.get("/investigations/{investigation_id}/suspects/{suspect_id}")
def get_suspect(
    investigation_id: int,
    suspect_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    state = db.query(InvestigationSuspectState).filter_by(investigation_id=inv.id, suspect_slug=suspect_id).first()
    if not state:
        raise not_found("Suspect not found")
    suspect = db.query(Suspect).filter_by(case_id=inv.case_id, slug=suspect_id).one()
    return {
        "slug": suspect.slug,
        "full_name": suspect.full_name,
        "age": suspect.age,
        "occupation": suspect.occupation,
        "public_bio": suspect.public_bio,
        "speech_style": suspect.speech_style,
        "personality_traits": suspect.personality_traits,
        "relationship_to_victim": suspect.relationship_to_victim,
        "public_motive": suspect.public_motive,
        "initial_alibi": suspect.initial_alibi,
        "portrait_palette": suspect.portrait_palette,
        "state": {
            "unlocked": state.unlocked,
            "trust": state.trust,
            "pressure": state.pressure,
            "interviewed_count": state.interviewed_count,
        },
    }


@router.get(
    "/investigations/{investigation_id}/suspects/{suspect_id}/messages",
    response_model=list[ChatMessageResponse],
)
def get_messages(
    investigation_id: int,
    suspect_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    msgs = (
        db.query(ConversationMessage)
        .filter_by(investigation_id=inv.id, suspect_slug=suspect_id)
        .order_by(ConversationMessage.id.asc())
        .all()
    )
    return [
        ChatMessageResponse(
            role=m.role,
            content=m.content,
            created_at=m.created_at,
            emotion=m.metadata_json.get("emotion", "calm"),
            contradiction_exposed=m.metadata_json.get("contradiction_exposed", False),
            unlocked_topics=m.metadata_json.get("unlocked_topics", []),
            ai_debug=m.metadata_json.get("ai_debug"),
        )
        for m in msgs
    ]


@router.post(
    "/investigations/{investigation_id}/suspects/{suspect_id}/messages",
    response_model=ChatMessageResponse,
)
async def send_message(
    investigation_id: int,
    suspect_id: str,
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    if len(payload.message) > settings.max_chat_message_length:
        raise HTTPException(status_code=422, detail="Message too long")
    state = db.query(InvestigationSuspectState).filter_by(investigation_id=inv.id, suspect_slug=suspect_id).first()
    if not state or not state.unlocked:
        raise HTTPException(status_code=403, detail="Suspect locked")

    key = f"{user.id}:{investigation_id}:{suspect_id}"
    if not rate_limiter.allow(key):
        raise HTTPException(status_code=429, detail="Too many requests")

    suspect = db.query(Suspect).filter_by(case_id=inv.case_id, slug=suspect_id).one()
    clues = engine.get_discovered_clues(db, inv.id)
    player = ConversationMessage(
        investigation_id=inv.id,
        suspect_slug=suspect.slug,
        role="player",
        content=payload.message[: settings.max_chat_message_length],
        metadata_json={},
    )
    db.add(player)

    ai, ai_debug = await dialogue.respond(
        db=db,
        inv=inv,
        suspect=suspect,
        state=state,
        player_message=payload.message,
        discovered_clues=clues,
        discussed_topics=set(inv.discussed_topics),
    )

    authorized_facts = set(suspect.known_facts)
    accepted_fact_ids = [f for f in ai.revealed_fact_ids if f in authorized_facts]
    rejected_fact_ids = [f for f in ai.revealed_fact_ids if f not in authorized_facts]

    contradiction_ids = engine.detect_contradictions(
        db,
        inv,
        suspect.slug,
        ai.dialogue,
        ai.referenced_clue_ids,
        ai.internal_flags.possible_contradiction,
    )
    engine.update_trust_pressure(state, bool(contradiction_ids))

    unlocked_topics: list[str] = []
    for topic_id in ai.suggested_topic_ids:
        topic = db.query(DialogueTopic).filter_by(case_id=inv.case_id, slug=topic_id).first()
        if topic and topic.slug not in inv.discussed_topics:
            unlocked_topics.append(topic.slug)
    if unlocked_topics:
        inv.discussed_topics = sorted(set(inv.discussed_topics).union(unlocked_topics))

    assistant = ConversationMessage(
        investigation_id=inv.id,
        suspect_slug=suspect.slug,
        role="suspect",
        content=ai.dialogue,
        metadata_json={
            "emotion": ai.emotion,
            "accepted_fact_ids": accepted_fact_ids,
            "rejected_fact_ids": rejected_fact_ids,
            "contradiction_exposed": bool(contradiction_ids),
            "contradiction_ids": contradiction_ids,
            "unlocked_topics": unlocked_topics,
            "ai_debug": {
                **ai_debug,
                "accepted_fact_ids": accepted_fact_ids,
                "rejected_fact_ids": rejected_fact_ids,
            },
        },
    )
    db.add(assistant)
    db.commit()
    db.refresh(assistant)

    debug_payload = assistant.metadata_json.get("ai_debug")
    if settings.app_env == "production":
        debug_payload = {
            "provider": debug_payload.get("provider"),
            "model": debug_payload.get("model"),
            "latency_ms": debug_payload.get("latency_ms"),
            "prompt_version": debug_payload.get("prompt_version"),
        }

    return ChatMessageResponse(
        role=assistant.role,
        content=assistant.content,
        created_at=assistant.created_at,
        emotion=assistant.metadata_json.get("emotion", "calm"),
        contradiction_exposed=assistant.metadata_json.get("contradiction_exposed", False),
        unlocked_topics=assistant.metadata_json.get("unlocked_topics", []),
        ai_debug=debug_payload,
    )


@router.post(
    "/investigations/{investigation_id}/suspects/{suspect_id}/confront",
    response_model=ChatMessageResponse,
)
async def confront_suspect(
    investigation_id: int,
    suspect_id: str,
    payload: ConfrontRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    msg = ChatMessageRequest(message=payload.message, evidence_clue_slug=payload.clue_slug)
    return await send_message(investigation_id, suspect_id, msg, db, user)


@router.get("/investigations/{investigation_id}/clues", response_model=list[ClueResponse])
def list_clues(investigation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    discovered = engine.get_discovered_clues(db, inv.id)
    all_clues = db.query(Clue).filter_by(case_id=inv.case_id).all()
    visible = [c for c in all_clues if c.slug in discovered]
    return [
        ClueResponse(
            clue_slug=c.slug,
            title=c.title,
            description=c.description,
            location_slug=c.location_slug,
            tags=c.tags,
        )
        for c in visible
    ]


@router.get(
    "/investigations/{investigation_id}/contradictions",
    response_model=list[ContradictionResponse],
)
def list_contradictions(
    investigation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    rows = (
        db.query(Contradiction)
        .filter(Contradiction.case_id == inv.case_id, Contradiction.slug.in_(inv.exposed_contradictions))
        .all()
    )
    return [ContradictionResponse(slug=r.slug, title=r.title, description=r.description) for r in rows]


@router.get("/investigations/{investigation_id}/notes", response_model=list[NoteResponse])
def get_notes(investigation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    rows = db.query(DetectiveNote).filter_by(investigation_id=inv.id).order_by(DetectiveNote.id.desc()).all()
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            body=n.body,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )
        for n in rows
    ]


@router.post("/investigations/{investigation_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    investigation_id: int,
    payload: NoteCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    note = DetectiveNote(investigation_id=inv.id, title=payload.title, body=payload.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteResponse(
        id=note.id,
        title=note.title,
        body=note.body,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.patch("/investigations/{investigation_id}/notes/{note_id}", response_model=NoteResponse)
def patch_note(
    investigation_id: int,
    note_id: int,
    payload: NotePatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    note = db.query(DetectiveNote).filter_by(investigation_id=inv.id, id=note_id).first()
    if not note:
        raise not_found("Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.body is not None:
        note.body = payload.body
    db.commit()
    db.refresh(note)
    return NoteResponse(
        id=note.id,
        title=note.title,
        body=note.body,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.delete("/investigations/{investigation_id}/notes/{note_id}", status_code=204)
def delete_note(investigation_id: int, note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    note = db.query(DetectiveNote).filter_by(investigation_id=inv.id, id=note_id).first()
    if not note:
        raise not_found("Note not found")
    db.delete(note)
    db.commit()


@router.get("/investigations/{investigation_id}/board", response_model=BoardPayload)
def get_board(investigation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    nodes = db.query(BoardNode).filter_by(investigation_id=inv.id).all()
    edges = db.query(BoardEdge).filter_by(investigation_id=inv.id).all()
    return BoardPayload(
        nodes=[
            {
                "id": n.node_id,
                "type": n.node_type,
                "label": n.label,
                "x": n.position_x,
                "y": n.position_y,
                "extra": n.extra,
            }
            for n in nodes
        ],
        edges=[{"id": e.edge_id, "source": e.source, "target": e.target, "label": e.label} for e in edges],
    )


@router.put("/investigations/{investigation_id}/board", response_model=BoardPayload)
def put_board(
    investigation_id: int,
    payload: BoardPayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    db.query(BoardNode).filter_by(investigation_id=inv.id).delete()
    db.query(BoardEdge).filter_by(investigation_id=inv.id).delete()

    for node in payload.nodes:
        db.add(
            BoardNode(
                investigation_id=inv.id,
                node_id=node.id,
                node_type=node.type,
                label=node.label,
                position_x=node.x,
                position_y=node.y,
                extra=node.extra,
            )
        )
    for edge in payload.edges:
        db.add(
            BoardEdge(
                investigation_id=inv.id,
                edge_id=edge.id,
                source=edge.source,
                target=edge.target,
                label=edge.label,
            )
        )
    db.commit()
    return payload


@router.post("/investigations/{investigation_id}/accusations", response_model=ResultResponse)
def submit_accusation(
    investigation_id: int,
    payload: AccusationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = owned_investigation_or_404(db, user, investigation_id)
    case = db.get(Case, inv.case_id)
    known_clues = engine.get_discovered_clues(db, inv.id)
    if not set(payload.supporting_clues).issubset(known_clues):
        raise HTTPException(status_code=422, detail="Supporting clues must be discovered first")

    score = ScoringService.score_accusation(
        case,
        payload.attacker_slug,
        payload.thief_slug,
        payload.motive,
        payload.supporting_clues,
    )
    ending_slug = ScoringService.pick_ending(score)

    existing = db.query(Accusation).filter_by(investigation_id=inv.id).first()
    if existing:
        db.delete(existing)
        db.flush()

    acc = Accusation(
        investigation_id=inv.id,
        attacker_slug=payload.attacker_slug,
        thief_slug=payload.thief_slug,
        motive=payload.motive,
        supporting_clues=payload.supporting_clues,
        explanation=payload.explanation,
        score=score,
        ending_slug=ending_slug,
    )
    inv.status = "completed"
    db.add(acc)

    ending = db.query(Ending).filter_by(case_id=case.id, slug=ending_slug).one()
    db.commit()
    return ResultResponse(
        score=score,
        ending_slug=ending.slug,
        ending_title=ending.title,
        ending_summary=ending.summary,
        canonical_revealed=True,
    )


@router.get("/investigations/{investigation_id}/result", response_model=ResultResponse)
def get_result(investigation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = owned_investigation_or_404(db, user, investigation_id)
    acc = db.query(Accusation).filter_by(investigation_id=inv.id).first()
    if not acc:
        raise not_found("Result not available")
    ending = db.query(Ending).filter_by(case_id=inv.case_id, slug=acc.ending_slug).one()
    return ResultResponse(
        score=acc.score,
        ending_slug=ending.slug,
        ending_title=ending.title,
        ending_summary=ending.summary,
        canonical_revealed=True,
    )
