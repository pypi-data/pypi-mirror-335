from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from nephyx.core.settings import BaseSettings

class DatabaseSessionManager:
    def __init__(self, settings: BaseSettings):
        self.db_engine = create_engine(str(settings.database_url))
        self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.db_engine)

    def get_db(self) -> Generator[Session, None, None]:
        db = self._session_factory()
        try:
            yield db
        finally:
            db.close()
