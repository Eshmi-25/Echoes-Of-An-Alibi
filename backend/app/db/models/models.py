from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class InvestigationStatus(str, Enum):
    active = "active"
    completed = "completed"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    investigations: Mapped[list["Investigation"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Case(Base, TimestampMixin):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    briefing: Mapped[str] = mapped_column(Text)
    max_actions: Mapped[int] = mapped_column(Integer, default=18)
    canonical_answer: Mapped[dict] = mapped_column(JSON)


class Suspect(Base, TimestampMixin):
    __tablename__ = "suspects"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    occupation: Mapped[str] = mapped_column(String(120))
    public_bio: Mapped[str] = mapped_column(Text)
    speech_style: Mapped[str] = mapped_column(Text)
    personality_traits: Mapped[list[str]] = mapped_column(JSON, default=list)
    relationship_to_victim: Mapped[str] = mapped_column(Text)
    public_motive: Mapped[str] = mapped_column(Text)
    hidden_motive: Mapped[str] = mapped_column(Text)
    initial_alibi: Mapped[str] = mapped_column(Text)
    true_timeline: Mapped[list[dict]] = mapped_column(JSON, default=list)
    known_facts: Mapped[list[str]] = mapped_column(JSON, default=list)
    secret_facts: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_lies: Mapped[list[str]] = mapped_column(JSON, default=list)
    forbidden_knowledge: Mapped[list[str]] = mapped_column(JSON, default=list)
    trust_thresholds: Mapped[dict] = mapped_column(JSON, default=dict)
    pressure_thresholds: Mapped[dict] = mapped_column(JSON, default=dict)
    confront_responses: Mapped[dict] = mapped_column(JSON, default=dict)
    topic_unlock_rules: Mapped[list[dict]] = mapped_column(JSON, default=list)
    portrait_palette: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (UniqueConstraint("case_id", "slug", name="uq_suspect_case_slug"),)


class Location(Base, TimestampMixin):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    unlock_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint("case_id", "slug", name="uq_location_case_slug"),)


class Clue(Base, TimestampMixin):
    __tablename__ = "clues"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    location_slug: Mapped[str] = mapped_column(String(100), index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    unlock_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_red_herring: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("case_id", "slug", name="uq_clue_case_slug"),)


class Fact(Base, TimestampMixin):
    __tablename__ = "facts"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    text: Mapped[str] = mapped_column(Text)
    visibility_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class DialogueTopic(Base, TimestampMixin):
    __tablename__ = "dialogue_topics"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(120))
    unlock_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Contradiction(Base, TimestampMixin):
    __tablename__ = "contradictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    trigger_rule: Mapped[dict] = mapped_column(JSON)


class Investigation(Base, TimestampMixin):
    __tablename__ = "investigations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default=InvestigationStatus.active.value)
    actions_remaining: Mapped[int] = mapped_column(Integer, default=18)
    visited_locations: Mapped[list[str]] = mapped_column(JSON, default=list)
    discussed_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    exposed_contradictions: Mapped[list[str]] = mapped_column(JSON, default=list)

    user: Mapped[User] = relationship(back_populates="investigations")
    clues: Mapped[list["InvestigationClue"]] = relationship(cascade="all, delete-orphan")


class InvestigationClue(Base, TimestampMixin):
    __tablename__ = "investigation_clues"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    clue_slug: Mapped[str] = mapped_column(String(100), index=True)

    __table_args__ = (UniqueConstraint("investigation_id", "clue_slug", name="uq_inv_clue"),)


class InvestigationSuspectState(Base, TimestampMixin):
    __tablename__ = "investigation_suspect_state"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    suspect_slug: Mapped[str] = mapped_column(String(100), index=True)
    unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    trust: Mapped[int] = mapped_column(Integer, default=50)
    pressure: Mapped[int] = mapped_column(Integer, default=0)
    interviewed_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("investigation_id", "suspect_slug", name="uq_inv_suspect_state"),)


class InvestigationLocationState(Base, TimestampMixin):
    __tablename__ = "investigation_location_state"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    location_slug: Mapped[str] = mapped_column(String(100), index=True)
    unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    searched_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("investigation_id", "location_slug", name="uq_inv_location_state"),)


class ConversationMessage(Base, TimestampMixin):
    __tablename__ = "conversation_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    suspect_slug: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class DetectiveNote(Base, TimestampMixin):
    __tablename__ = "detective_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text)


class BoardNode(Base, TimestampMixin):
    __tablename__ = "board_nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    node_id: Mapped[str] = mapped_column(String(80), index=True)
    node_type: Mapped[str] = mapped_column(String(20))
    label: Mapped[str] = mapped_column(String(120))
    position_x: Mapped[int] = mapped_column(Integer)
    position_y: Mapped[int] = mapped_column(Integer)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (UniqueConstraint("investigation_id", "node_id", name="uq_board_node"),)


class BoardEdge(Base, TimestampMixin):
    __tablename__ = "board_edges"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    edge_id: Mapped[str] = mapped_column(String(80), index=True)
    source: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(80))
    label: Mapped[str] = mapped_column(String(120), default="")

    __table_args__ = (UniqueConstraint("investigation_id", "edge_id", name="uq_board_edge"),)


class Accusation(Base, TimestampMixin):
    __tablename__ = "accusations"
    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), unique=True, index=True)
    attacker_slug: Mapped[str] = mapped_column(String(100))
    thief_slug: Mapped[str] = mapped_column(String(100))
    motive: Mapped[str] = mapped_column(Text)
    supporting_clues: Mapped[list[str]] = mapped_column(JSON)
    explanation: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer)
    ending_slug: Mapped[str] = mapped_column(String(100), index=True)


class Ending(Base, TimestampMixin):
    __tablename__ = "endings"
    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(160))
    summary: Mapped[str] = mapped_column(Text)
    min_score: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("case_id", "slug", name="uq_ending_case_slug"),)
