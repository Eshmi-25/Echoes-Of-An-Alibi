import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.models import Case, Clue, Contradiction, DialogueTopic, Ending, Fact, Location, Suspect
from app.db.session import SessionLocal, engine


def load_seed(session: Session) -> None:
    path = Path(__file__).with_name("midnight_gallery.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    existing = session.query(Case).filter_by(slug=data["case"]["slug"]).first()
    if existing:
        return

    case_data = data["case"]
    case = Case(
        slug=case_data["slug"],
        title=case_data["title"],
        briefing=case_data["briefing"],
        max_actions=case_data["max_actions"],
        canonical_answer=case_data["canonical_answer"],
    )
    session.add(case)
    session.flush()

    for item in data["locations"]:
        session.add(Location(case_id=case.id, **item))

    for item in data["suspects"]:
        session.add(Suspect(case_id=case.id, **item))

    for item in data["clues"]:
        session.add(Clue(case_id=case.id, **item))

    for item in data["facts"]:
        session.add(Fact(case_id=case.id, **item))

    for item in data["topics"]:
        session.add(DialogueTopic(case_id=case.id, **item))

    for item in data["contradictions"]:
        session.add(Contradiction(case_id=case.id, **item))

    for item in data["endings"]:
        session.add(Ending(case_id=case.id, **item))


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        load_seed(session)
        session.commit()


if __name__ == "__main__":
    main()
