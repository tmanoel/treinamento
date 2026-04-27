from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import repository
from app.models import Emprestimo, Livro
from app.schemas import EmprestimoCreate, LivroCreate


def criar_livro(db: Session, dados: LivroCreate) -> Livro:
    if repository.existe_por_titulo_autor(db, dados.titulo, dados.autor):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um livro com este título e autor",
        )
    livro = Livro(**dados.model_dump())
    return repository.criar(db, livro)


def listar_livros(
    db: Session,
    titulo: str | None = None,
    autor: str | None = None,
    editora: str | None = None,
    ano_publicacao: int | None = None,
    lido: bool | None = None,
) -> list[Livro]:
    return repository.listar(
        db,
        titulo=titulo,
        autor=autor,
        editora=editora,
        ano_publicacao=ano_publicacao,
        lido=lido,
    )


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


def remover_livro(db: Session, livro_id: int) -> None:
    livro = buscar_livro(db, livro_id)
    repository.remover(db, livro)


def emprestar_livro(db: Session, livro_id: int, dados: EmprestimoCreate) -> Emprestimo:
    livro = buscar_livro(db, livro_id)

    if dados.data_emprestimo < livro.created_at.replace(microsecond=0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_emprestimo não pode ser anterior à criação do livro",
        )

    if repository.emprestimo_ativo(db, livro_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Livro já está emprestado",
        )

    emprestimo = Emprestimo(
        livro_id=livro_id,
        emprestado_para=dados.emprestado_para,
        data_emprestimo=dados.data_emprestimo,
    )
    return repository.criar_emprestimo(db, emprestimo)
