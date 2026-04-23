from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = "sqlite:///./biblioteca.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _utc_now() -> datetime:
    return datetime.now(tz=UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Livro(Base):
    __tablename__ = "livros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    autor: Mapped[str] = mapped_column(String, nullable=False)
    editora: Mapped[str] = mapped_column(String, nullable=False)
    ano_publicacao: Mapped[int] = mapped_column(Integer, nullable=False)
    lido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now, onupdate=_utc_now
    )
