from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import service
from app.models import SessionLocal
from app.schemas import LivroCreate, LivroResponse

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
