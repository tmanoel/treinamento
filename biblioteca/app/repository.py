from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Emprestimo, Livro


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


def listar(
    db: Session,
    titulo: str | None = None,
    autor: str | None = None,
    editora: str | None = None,
    ano_publicacao: int | None = None,
    lido: bool | None = None,
) -> list[Livro]:
    query = db.query(Livro)
    if titulo is not None:
        query = query.filter(Livro.titulo.ilike(f"%{titulo}%"))
    if autor is not None:
        query = query.filter(Livro.autor.ilike(f"%{autor}%"))
    if editora is not None:
        query = query.filter(Livro.editora.ilike(f"%{editora}%"))
    if ano_publicacao is not None:
        query = query.filter(Livro.ano_publicacao == ano_publicacao)
    if lido is not None:
        query = query.filter(Livro.lido == lido)
    return query.order_by(Livro.id).all()


def buscar_por_id(db: Session, livro_id: int) -> Livro | None:
    return db.query(Livro).filter(Livro.id == livro_id).first()


def atualizar(db: Session, livro: Livro) -> Livro:
    db.commit()
    db.refresh(livro)
    return livro


def remover(db: Session, livro: Livro) -> None:
    db.delete(livro)
    db.commit()


def emprestimo_ativo(db: Session, livro_id: int) -> Emprestimo | None:
    return (
        db.query(Emprestimo)
        .filter(Emprestimo.livro_id == livro_id, Emprestimo.data_devolucao.is_(None))
        .first()
    )


def criar_emprestimo(db: Session, emprestimo: Emprestimo) -> Emprestimo:
    db.add(emprestimo)
    db.commit()
    db.refresh(emprestimo)
    return emprestimo


def atualizar_emprestimo(db: Session, emprestimo: Emprestimo) -> Emprestimo:
    db.commit()
    db.refresh(emprestimo)
    return emprestimo


def listar_emprestimos_do_livro(db: Session, livro_id: int) -> list[Emprestimo]:
    return (
        db.query(Emprestimo)
        .filter(Emprestimo.livro_id == livro_id)
        .order_by(Emprestimo.data_emprestimo.desc())
        .all()
    )
