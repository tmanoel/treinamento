from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import repository
from app.models import Livro
from app.schemas import LivroCreate


def criar_livro(db: Session, dados: LivroCreate) -> Livro:
    if repository.existe_por_titulo_autor(db, dados.titulo, dados.autor):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um livro com este título e autor",
        )
    livro = Livro(**dados.model_dump())
    return repository.criar(db, livro)
