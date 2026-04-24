from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import service
from app.models import SessionLocal
from app.schemas import LivroCreate, LivroResponse, LivroUpdate

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


@router.get("/livros", response_model=list[LivroResponse])
def listar_livros(db: Session = Depends(get_db)):
    return service.listar_livros(db)


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
