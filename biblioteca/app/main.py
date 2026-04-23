from fastapi import APIRouter, FastAPI

from app.models import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Biblioteca Pessoal")

api_router = APIRouter(prefix="/api")


@api_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
