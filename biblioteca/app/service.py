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


def listar_livros(db: Session) -> list[Livro]:
    return repository.listar(db)


def buscar_livro(db: Session, livro_id: int) -> Livro:
    livro = repository.buscar_por_id(db, livro_id)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado",
        )
    return livro


def atualizar_livro(db: Session, livro_id: int, campos: dict) -> Livro:
    livro = buscar_livro(db, livro_id)

    novo_titulo = campos.get("titulo", livro.titulo)
    novo_autor = campos.get("autor", livro.autor)
    if ("titulo" in campos or "autor" in campos) and repository.existe_por_titulo_autor(
        db, novo_titulo, novo_autor, excluir_id=livro_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um livro com este título e autor",
        )

    for campo, valor in campos.items():
        setattr(livro, campo, valor)
    return repository.atualizar(db, livro)
