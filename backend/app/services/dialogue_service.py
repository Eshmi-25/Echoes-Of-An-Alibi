from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models.models import ConversationMessage, Investigation, InvestigationSuspectState, Suspect
from app.prompts.templates import CONFRONT_TEMPLATE, FOLLOW_UP_TEMPLATE, INITIAL_INTERVIEW_TEMPLATE
from app.services.ai_service import AIResponse, AIService


class DialogueService:
    def __init__(self, settings: Settings) -> None:
        self.ai = AIService(settings)
        self.settings = settings

    async def respond(
        self,
        db: Session,
        inv: Investigation,
        suspect: Suspect,
        state: InvestigationSuspectState,
        player_message: str,
        discovered_clues: set[str],
        discussed_topics: set[str],
        is_confrontation: bool = False,
        evidence_slug: str | None = None,
    ) -> tuple[AIResponse, dict]:
        history = (
            db.query(ConversationMessage)
            .filter_by(investigation_id=inv.id, suspect_slug=suspect.slug)
            .order_by(ConversationMessage.id.asc())
            .all()
        )
        context = {
            "public_identity": suspect.full_name,
            "personality": suspect.personality_traits,
            "known_alibi": suspect.initial_alibi,
            "actual_movements": suspect.true_timeline,
            "may_reveal": suspect.known_facts,
            "must_not_know": suspect.forbidden_knowledge,
            "allowed_lies": suspect.allowed_lies,
            "discovered_clues": sorted(discovered_clues),
            "unlocked_topics": sorted(discussed_topics),
            "trust": state.trust,
            "pressure": state.pressure,
        }

        if is_confrontation:
            prompt = CONFRONT_TEMPLATE.format(
                suspect_name=suspect.full_name,
                clue_slug=evidence_slug or "unknown",
                context=context,
                question=player_message,
            )
        elif state.interviewed_count == 0:
            prompt = INITIAL_INTERVIEW_TEMPLATE.format(
                suspect_name=suspect.full_name,
                context=context,
                question=player_message,
            )
        else:
            compact_history = [f"{m.role}: {m.content}" for m in history[-6:]]
            prompt = FOLLOW_UP_TEMPLATE.format(
                suspect_name=suspect.full_name,
                context=context,
                history=compact_history,
                question=player_message,
            )

        fallback = {
            "dialogue": self._fallback_text(suspect.full_name, player_message, state.pressure),
            "emotion": "guarded" if state.pressure > 40 else "calm",
            "revealed_fact_ids": suspect.known_facts[:1],
            "referenced_clue_ids": [evidence_slug] if evidence_slug else [],
            "suggested_topic_ids": ["timeline-gap"],
            "internal_flags": {
                "evasive": state.pressure > 60,
                "possible_contradiction": "11:47" in player_message or "restoration" in player_message.lower(),
            },
        }
        return await self.ai.generate(prompt, fallback)

    @staticmethod
    def _fallback_text(name: str, question: str, pressure: int) -> str:
        if pressure > 65:
            return f"{name} hesitates. 'I already told you what I saw. Ask about the hallway clock.'"
        if "where" in question.lower():
            return f"{name} says, 'I was near the east corridor before midnight, then moved on.'"
        return f"{name} replies, 'You're circling close, detective. Check the access records.'"
