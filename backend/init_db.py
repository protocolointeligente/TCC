from database import Base, engine
import db_models  # noqa: F401 — registers all ORM models with Base.metadata
import cep_models  # noqa: F401
import instrument_models  # noqa: F401
import advanced_cep_models  # noqa: F401

Base.metadata.create_all(bind=engine)
print("Banco criado com sucesso.")
