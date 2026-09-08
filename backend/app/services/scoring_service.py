from app.db.models.models import Case


class ScoringService:
    @staticmethod
    def score_accusation(
        case: Case,
        attacker_slug: str,
        thief_slug: str,
        motive: str,
        supporting_clues: list[str],
    ) -> int:
        canonical = case.canonical_answer
        score = 0
        if attacker_slug == canonical["attacker_slug"]:
            score += 35
        if thief_slug == canonical["thief_slug"]:
            score += 35
        if motive.strip().lower() == canonical["motive"].strip().lower():
            score += 20

        required = set(canonical["required_clue_slugs"])
        provided = set(supporting_clues)
        score += min(10, len(required.intersection(provided)) * 5)
        return min(100, score)

    @staticmethod
    def pick_ending(score: int) -> str:
        if score >= 90:
            return "truth-unveiled"
        if score >= 70:
            return "close-but-clouded"
        if score >= 45:
            return "frayed-case"
        return "cold-trail"
