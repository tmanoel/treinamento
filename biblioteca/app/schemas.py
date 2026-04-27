from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, StrictBool, field_serializer, field_validator

MIN_ANO = 1400


def _ano_atual() -> int:
    return datetime.now(tz=UTC).year


def _msg_ano_invalido() -> str:
    return f"ano_publicacao deve ser um número inteiro entre {MIN_ANO} e {_ano_atual()}"


def _validar_ano(v: object) -> int:
    if not isinstance(v, int) or isinstance(v, bool):
        raise ValueError(_msg_ano_invalido())
    if v < MIN_ANO or v > _ano_atual():
        raise ValueError(_msg_ano_invalido())
    return v


class LivroCreate(BaseModel):
    titulo: str
    autor: str
    editora: str
    ano_publicacao: int
    lido: StrictBool = False

    @field_validator("titulo", "autor", "editora", mode="before")
    @classmethod
    def _obrigatorio(cls, v: object, info) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"{info.field_name} é obrigatório")
        return v.strip()

    @field_validator("ano_publicacao", mode="before")
    @classmethod
    def _ano(cls, v: object) -> int:
        return _validar_ano(v)


class LivroUpdate(BaseModel):
    lido: bool | None = None
    ano_publicacao: int | None = None
    titulo: str | None = None
    autor: str | None = None
    editora: str | None = None

    @field_validator("lido", mode="before")
    @classmethod
    def _lido_bool(cls, v: object) -> bool | None:
        if v is None:
            return None
        if not isinstance(v, bool):
            raise ValueError("lido deve ser true ou false")
        return v

    @field_validator("ano_publicacao", mode="before")
    @classmethod
    def _ano(cls, v: object) -> int | None:
        if v is None:
            return None
        return _validar_ano(v)

    @field_validator("titulo", "autor", "editora", mode="before")
    @classmethod
    def _nao_vazio(cls, v: object, info) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"{info.field_name} não pode ser vazio")
        return v.strip()


class LivroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    autor: str
    editora: str
    ano_publicacao: int
    lido: bool
    emprestado: bool
    emprestado_para: str | None
    data_emprestimo: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def _iso_utc(self, v: datetime) -> str:
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")

    @field_serializer("data_emprestimo")
    def _iso_utc_opt(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%dT%H:%M:%SZ") if v is not None else None


def _validar_data_nao_futura(v: datetime, campo: str) -> datetime:
    agora = datetime.now(tz=UTC).replace(tzinfo=None)
    valor = v.replace(tzinfo=None) if v.tzinfo is not None else v
    if valor > agora:
        raise ValueError(f"{campo} não pode ser futura")
    return valor


class EmprestimoCreate(BaseModel):
    emprestado_para: str
    data_emprestimo: datetime

    @field_validator("emprestado_para", mode="before")
    @classmethod
    def _emprestado_para_obrigatorio(cls, v: object) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("emprestado_para é obrigatório")
        return v.strip()

    @field_validator("data_emprestimo", mode="after")
    @classmethod
    def _data_emprestimo_nao_futura(cls, v: datetime) -> datetime:
        return _validar_data_nao_futura(v, "data_emprestimo")


class EmprestimoClose(BaseModel):
    data_devolucao: datetime

    @field_validator("data_devolucao", mode="after")
    @classmethod
    def _data_devolucao_nao_futura(cls, v: datetime) -> datetime:
        return _validar_data_nao_futura(v, "data_devolucao")


class EmprestimoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    livro_id: int
    emprestado_para: str
    data_emprestimo: datetime
    data_devolucao: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("data_emprestimo", "created_at", "updated_at")
    def _iso_utc(self, v: datetime) -> str:
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")

    @field_serializer("data_devolucao")
    def _iso_utc_opt(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%dT%H:%M:%SZ") if v is not None else None
