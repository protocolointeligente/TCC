"""
Seed the research_instruments table from the static database.
Safe to run multiple times: existing rows are skipped, new ones are inserted.
"""
from database import SessionLocal
from instrument_models import ResearchInstrument
from services.instruments_database import INSTRUMENT_DATABASE


def seed():
    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0
        for data in INSTRUMENT_DATABASE:
            exists = db.query(ResearchInstrument).filter(ResearchInstrument.id == data["id"]).first()
            if exists:
                skipped += 1
                continue
            instrument = ResearchInstrument(
                id=data["id"],
                name=data["name"],
                full_name=data.get("full_name"),
                area=data.get("area"),
                construct=data.get("construct"),
                objective_keywords=data.get("objective_keywords", []),
                original_reference=data.get("original_reference"),
                brazilian_validation_reference=data.get("brazilian_validation_reference"),
                validated_population_brazil=data.get("validated_population_brazil"),
                license_use=data.get("license_use"),
                scoring=data.get("scoring"),
                application_mode=data.get("application_mode", []),
                ethical_notes=data.get("ethical_notes", []),
                is_active=True,
            )
            db.add(instrument)
            inserted += 1
        db.commit()
        print(f"Instrumentos inseridos: {inserted} | Já existiam: {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
