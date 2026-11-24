import json
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = ROOT_DIR / "sahaay.db"

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_DB_PATH}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    """Yield a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_data(db) -> None:
    """Seed curated schemes and sample registered NGOs when tables are empty."""
    from ..models.db_models import NGO, Scheme

    if db.query(Scheme).count() == 0:
        schemes_path = ROOT_DIR / "data" / "schemes" / "schemes.json"
        if schemes_path.exists():
            raw_schemes = json.loads(schemes_path.read_text(encoding="utf-8"))
            for item in raw_schemes:
                db.add(
                    Scheme(
                        slug=item["slug"],
                        name=item["name"],
                        category=item["category"],
                        description=item["description"],
                        benefits=item["benefits"],
                        eligibility_rules_json=json.dumps(item["eligibility_rules"]),
                        application_guidance=item["application_guidance"],
                        source_url=item["source_url"],
                        last_reviewed=item["last_reviewed"],
                    )
                )

    if db.query(NGO).count() == 0:
        ngos_path = ROOT_DIR / "data" / "ngos.json"
        if ngos_path.exists():
            raw_ngos = json.loads(ngos_path.read_text(encoding="utf-8"))
            for item in raw_ngos:
                db.add(
                    NGO(
                        name=item["name"],
                        location=item["location"],
                        city=item["city"],
                        contact_email=item["contact_email"],
                        focus_areas=item["focus_areas"],
                        is_available=item.get("is_available", True),
                    )
                )

    db.commit()


def init_db() -> None:
    """Create tables and populate initial curated datasets."""
    from ..models import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
