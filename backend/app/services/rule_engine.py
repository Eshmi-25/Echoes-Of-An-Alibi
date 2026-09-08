from collections.abc import Callable

from app.db.models.models import Investigation, InvestigationSuspectState


class RuleEngine:
    def evaluate(
        self,
        rule: dict | None,
        inv: Investigation,
        clue_slugs: set[str],
        suspect_states: dict[str, InvestigationSuspectState],
    ) -> bool:
        if not rule:
            return True

        op = rule.get("op")
        if op == "and":
            return all(self.evaluate(item, inv, clue_slugs, suspect_states) for item in rule.get("rules", []))
        if op == "or":
            return any(self.evaluate(item, inv, clue_slugs, suspect_states) for item in rule.get("rules", []))

        handlers: dict[str, Callable[[dict], bool]] = {
            "has_clue": lambda r: r.get("clue") in clue_slugs,
            "interviewed_suspect": lambda r: suspect_states.get(r.get("suspect"), None) is not None
            and suspect_states[r["suspect"]].interviewed_count > 0,
            "visited_location": lambda r: r.get("location") in set(inv.visited_locations),
            "trust_gt": lambda r: self._suspect_value(suspect_states, r, "trust") > int(r.get("value", 0)),
            "pressure_gt": lambda r: self._suspect_value(suspect_states, r, "pressure") > int(r.get("value", 0)),
            "topic_discussed": lambda r: r.get("topic") in set(inv.discussed_topics),
            "contradiction_exposed": lambda r: r.get("contradiction") in set(inv.exposed_contradictions),
        }

        handler = handlers.get(op)
        if not handler:
            return False
        return bool(handler(rule))

    @staticmethod
    def _suspect_value(states: dict[str, InvestigationSuspectState], rule: dict, field: str) -> int:
        slug = rule.get("suspect")
        state = states.get(slug)
        if not state:
            return 0
        return int(getattr(state, field, 0))
