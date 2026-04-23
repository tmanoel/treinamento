from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Livro


def existe_por_titulo_autor(db: Session, titulo: str, autor: str) -> bool:
    return (
        db.query(Livro)
        .filter(
            func.lower(Livro.titulo) == titulo.lower(),
            func.lower(Livro.autor) == autor.lower(),
        )
        .first()
        is not None
    )


def criar(db: Session, livro: Livro) -> Livro:
    db.add(livro)
    db.commit()
    db.refresh(livro)
    return livro
