from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Livro


def existe_por_titulo_autor(
    db: Session, titulo: str, autor: str, excluir_id: int | None = None
) -> bool:
    query = db.query(Livro).filter(
        func.lower(Livro.titulo) == titulo.lower(),
        func.lower(Livro.autor) == autor.lower(),
    )
    if excluir_id is not None:
        query = query.filter(Livro.id != excluir_id)
    return query.first() is not None


def criar(db: Session, livro: Livro) -> Livro:
    db.add(livro)
    db.commit()
    db.refresh(livro)
    return livro


def listar(db: Session) -> list[Livro]:
    return db.query(Livro).order_by(Livro.id).all()


def buscar_por_id(db: Session, livro_id: int) -> Livro | None:
    return db.query(Livro).filter(Livro.id == livro_id).first()


def atualizar(db: Session, livro: Livro) -> Livro:
    db.commit()
    db.refresh(livro)
    return livro
