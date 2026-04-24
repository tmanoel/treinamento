from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models import Base, engine
from app.router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Biblioteca Pessoal")
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def _traduzir_erro_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    erros = exc.errors()
    if not erros:
        return JSONResponse(status_code=400, content={"detail": "Requisição inválida"})

    err = erros[0]
    tipo = err.get("type", "")
    loc = err.get("loc", [])
    campo = loc[-1] if loc else ""

    if tipo == "missing" and isinstance(campo, str):
        mensagem = f"{campo} é obrigatório"
    elif tipo == "int_parsing" and isinstance(campo, str):
        mensagem = f"{campo} deve ser um número inteiro"
    else:
        mensagem = err.get("msg", "").removeprefix("Value error, ")

    return JSONResponse(status_code=400, content={"detail": mensagem})
