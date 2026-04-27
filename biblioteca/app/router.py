from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import service
from app.models import SessionLocal
from app.schemas import (
    EmprestimoClose,
    EmprestimoCreate,
    EmprestimoResponse,
    LivroCreate,
    LivroResponse,
    LivroUpdate,
)

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/livros",
    response_model=LivroResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_livro(payload: LivroCreate, db: Session = Depends(get_db)):
    return service.criar_livro(db, payload)


def _coerce_bool_query(valor: str | None, campo: str) -> bool | None:
    if valor is None:
        return None
    normalizado = valor.lower()
    if normalizado == "true":
        return True
    if normalizado == "false":
        return False
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{campo} deve ser true ou false",
    )


def _coerce_data_query(valor: str | None, campo: str) -> datetime | None:
    if valor is None:
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{campo} deve ser uma data ISO 8601 válida",
        ) from exc


@router.get("/livros", response_model=list[LivroResponse])
def listar_livros(
    titulo: str | None = None,
    autor: str | None = None,
    editora: str | None = None,
    ano_publicacao: int | None = None,
    lido: str | None = None,
    emprestado: str | None = None,
    emprestado_para: str | None = None,
    emprestado_desde: str | None = None,
    emprestado_ate: str | None = None,
    db: Session = Depends(get_db),
):
    return service.listar_livros(
        db,
        titulo=titulo,
        autor=autor,
        editora=editora,
        ano_publicacao=ano_publicacao,
        lido=_coerce_bool_query(lido, "lido"),
        emprestado=_coerce_bool_query(emprestado, "emprestado"),
        emprestado_para=emprestado_para,
        emprestado_desde=_coerce_data_query(emprestado_desde, "emprestado_desde"),
        emprestado_ate=_coerce_data_query(emprestado_ate, "emprestado_ate"),
    )


@router.get("/livros/{livro_id}", response_model=LivroResponse)
def buscar_livro(livro_id: int, db: Session = Depends(get_db)):
    return service.buscar_livro(db, livro_id)


@router.patch("/livros/{livro_id}", response_model=LivroResponse)
def atualizar_livro(livro_id: int, payload: LivroUpdate, db: Session = Depends(get_db)):
    campos = payload.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe ao menos um campo para atualizar",
        )
    return service.atualizar_livro(db, livro_id, campos)


@router.delete("/livros/{livro_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_livro(livro_id: int, db: Session = Depends(get_db)) -> None:
    service.remover_livro(db, livro_id)


@router.post(
    "/livros/{livro_id}/emprestimos",
    response_model=EmprestimoResponse,
    status_code=status.HTTP_201_CREATED,
)
def emprestar_livro(
    livro_id: int, payload: EmprestimoCreate, db: Session = Depends(get_db)
):
    return service.emprestar_livro(db, livro_id, payload)


@router.delete(
    "/livros/{livro_id}/emprestimos",
    response_model=EmprestimoResponse,
)
def devolver_livro(
    livro_id: int, payload: EmprestimoClose, db: Session = Depends(get_db)
):
    return service.devolver_livro(db, livro_id, payload)


@router.get(
    "/livros/{livro_id}/emprestimos",
    response_model=list[EmprestimoResponse],
)
def listar_emprestimos(livro_id: int, db: Session = Depends(get_db)):
    return service.listar_emprestimos(db, livro_id)
