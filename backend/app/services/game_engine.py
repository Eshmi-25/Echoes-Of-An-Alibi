from sqlalchemy.orm import Session

from app.db.models.models import (
    Clue,
    Contradiction,
    Investigation,
    InvestigationClue,
    InvestigationLocationState,
    InvestigationSuspectState,
    Location,
    Suspect,
)
from app.services.rule_engine import RuleEngine


class GameEngine:
    def __init__(self) -> None:
        self.rules = RuleEngine()

    def consume_action(self, inv: Investigation) -> bool:
        if inv.actions_remaining <= 0:
            return False
        inv.actions_remaining -= 1
        return True

    def get_discovered_clues(self, db: Session, investigation_id: int) -> set[str]:
        rows = db.query(InvestigationClue).filter_by(investigation_id=investigation_id).all()
        return {r.clue_slug for r in rows}

    def get_suspect_states(self, db: Session, investigation_id: int) -> dict[str, InvestigationSuspectState]:
        rows = db.query(InvestigationSuspectState).filter_by(investigation_id=investigation_id).all()
        return {r.suspect_slug: r for r in rows}

    def sync_unlocks(self, db: Session, inv: Investigation) -> tuple[list[str], list[str]]:
        clue_slugs = self.get_discovered_clues(db, inv.id)
        suspect_states = self.get_suspect_states(db, inv.id)

        new_locations: list[str] = []
        for loc_state in db.query(InvestigationLocationState).filter_by(investigation_id=inv.id).all():
            if loc_state.unlocked:
                continue
            location = db.query(Location).filter_by(case_id=inv.case_id, slug=loc_state.location_slug).one()
            if self.rules.evaluate(location.unlock_rule, inv, clue_slugs, suspect_states):
                loc_state.unlocked = True
                new_locations.append(loc_state.location_slug)

        new_suspects: list[str] = []
        for sus_state in db.query(InvestigationSuspectState).filter_by(investigation_id=inv.id).all():
            if sus_state.unlocked:
                continue
            suspect = db.query(Suspect).filter_by(case_id=inv.case_id, slug=sus_state.suspect_slug).one()
            unlock_rule = suspect.trust_thresholds.get("unlock_rule") if suspect.trust_thresholds else None
            if self.rules.evaluate(unlock_rule, inv, clue_slugs, suspect_states):
                sus_state.unlocked = True
                new_suspects.append(sus_state.suspect_slug)

        return new_locations, new_suspects

    def search_location(self, db: Session, inv: Investigation, location_slug: str) -> tuple[list[str], list[str], list[str]]:
        if not self.consume_action(inv):
            return [], [], []
        state = db.query(InvestigationLocationState).filter_by(investigation_id=inv.id, location_slug=location_slug).one()
        state.searched_count += 1
        if location_slug not in inv.visited_locations:
            inv.visited_locations = [*inv.visited_locations, location_slug]

        discovered = self.get_discovered_clues(db, inv.id)
        suspect_states = self.get_suspect_states(db, inv.id)
        found: list[str] = []

        clues = db.query(Clue).filter_by(case_id=inv.case_id, location_slug=location_slug).all()
        for clue in clues:
            if clue.slug in discovered:
                continue
            if not self.rules.evaluate(clue.unlock_rule, inv, discovered, suspect_states):
                continue
            db.add(InvestigationClue(investigation_id=inv.id, clue_slug=clue.slug))
            discovered.add(clue.slug)
            found.append(clue.slug)

        db.flush()
        new_locations, new_suspects = self.sync_unlocks(db, inv)
        return found, new_locations, new_suspects

    def update_trust_pressure(self, state: InvestigationSuspectState, exposed_contradiction: bool) -> None:
        if exposed_contradiction:
            state.pressure = min(100, state.pressure + 18)
            state.trust = max(0, state.trust - 12)
        else:
            state.pressure = min(100, state.pressure + 4)
            state.trust = min(100, state.trust + 2)
        state.interviewed_count += 1

    def detect_contradictions(
        self,
        db: Session,
        inv: Investigation,
        suspect_slug: str,
        message_text: str,
        referenced_clues: list[str],
        possible_flag: bool,
    ) -> list[str]:
        discovered = self.get_discovered_clues(db, inv.id)
        exposed = set(inv.exposed_contradictions)
        found: list[str] = []

        all_rules = db.query(Contradiction).filter_by(case_id=inv.case_id).all()
        states = self.get_suspect_states(db, inv.id)

        for c in all_rules:
            if c.slug in exposed:
                continue
            trigger = c.trigger_rule
            suspect_match = trigger.get("suspect") == suspect_slug
            clue_match = trigger.get("requires_clue") in discovered if trigger.get("requires_clue") else True
            keyword = trigger.get("keyword")
            keyword_match = keyword.lower() in message_text.lower() if keyword else True
            hard_flag = trigger.get("requires_possible_flag", False)
            flag_match = (possible_flag is True) if hard_flag else True
            references_match = (
                trigger.get("referenced_clue") in referenced_clues if trigger.get("referenced_clue") else True
            )
            if suspect_match and clue_match and keyword_match and flag_match and references_match:
                exposed.add(c.slug)
                found.append(c.slug)

        if found:
            inv.exposed_contradictions = sorted(exposed)
        return found
