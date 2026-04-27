from datetime import datetime

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models import Emprestimo, Livro


def _anexar_emprestimo(livro: Livro, emp: Emprestimo | None) -> Livro:
    livro.emprestado = emp is not None
    livro.emprestado_para = emp.emprestado_para if emp else None
    livro.data_emprestimo = emp.data_emprestimo if emp else None
    return livro


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
    return _anexar_emprestimo(livro, None)


def listar(
    db: Session,
    titulo: str | None = None,
    autor: str | None = None,
    editora: str | None = None,
    ano_publicacao: int | None = None,
    lido: bool | None = None,
    emprestado: bool | None = None,
    emprestado_para: str | None = None,
    emprestado_desde: datetime | None = None,
    emprestado_ate: datetime | None = None,
) -> list[Livro]:
    join_cond = and_(
        Emprestimo.livro_id == Livro.id,
        Emprestimo.data_devolucao.is_(None),
    )
    query = db.query(Livro, Emprestimo).outerjoin(Emprestimo, join_cond)

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
    if emprestado is True:
        query = query.filter(Emprestimo.id.isnot(None))
    elif emprestado is False:
        query = query.filter(Emprestimo.id.is_(None))
    if emprestado_para is not None:
        query = query.filter(Emprestimo.emprestado_para.ilike(f"%{emprestado_para}%"))
    if emprestado_desde is not None:
        query = query.filter(Emprestimo.data_emprestimo >= emprestado_desde)
    if emprestado_ate is not None:
        query = query.filter(Emprestimo.data_emprestimo <= emprestado_ate)

    resultado = query.order_by(Livro.id).all()
    return [_anexar_emprestimo(livro, emp) for livro, emp in resultado]


def buscar_por_id(db: Session, livro_id: int) -> Livro | None:
    livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if livro is None:
        return None
    return _anexar_emprestimo(livro, emprestimo_ativo(db, livro_id))


def atualizar(db: Session, livro: Livro) -> Livro:
    db.commit()
    db.refresh(livro)
    return _anexar_emprestimo(livro, emprestimo_ativo(db, livro.id))


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
