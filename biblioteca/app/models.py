from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL = "sqlite:///./biblioteca.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(Engine, "connect")
def _ativa_fk_sqlite(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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

    emprestimos: Mapped[list["Emprestimo"]] = relationship(
        back_populates="livro",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    livro_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("livros.id", ondelete="CASCADE"),
        nullable=False,
    )
    emprestado_para: Mapped[str] = mapped_column(String, nullable=False)
    data_emprestimo: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_devolucao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now, onupdate=_utc_now
    )

    livro: Mapped["Livro"] = relationship(back_populates="emprestimos")

    __table_args__ = (Index("ix_emprestimos_livro_id", "livro_id"),)
