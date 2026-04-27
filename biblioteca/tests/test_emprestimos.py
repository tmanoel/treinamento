from datetime import UTC, datetime, timedelta

import pytest

LIVRO_BASE = {
    "titulo": "O Hobbit",
    "autor": "J.R.R. Tolkien",
    "editora": "HarperCollins",
    "ano_publicacao": 1937,
}


def _agora_iso() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def livro(client):
    """Cria um livro e devolve a resposta JSON."""
    return client.post("/api/livros", json=LIVRO_BASE).json()


# --- US08: Emprestar livro ---

def test_us08_empresta_201(client, livro):
    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["livro_id"] == livro["id"]
    assert body["emprestado_para"] == "Maria"
    assert body["data_devolucao"] is None
    assert isinstance(body["id"], int)


def test_us08_400_emprestado_para_ausente(client, livro):
    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_emprestimo": _agora_iso()},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "emprestado_para é obrigatório"


def test_us08_400_emprestado_para_vazio(client, livro):
    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "   ", "data_emprestimo": _agora_iso()},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "emprestado_para é obrigatório"


def test_us08_400_data_emprestimo_futura(client, livro):
    futuro = _iso(datetime.now(tz=UTC) + timedelta(days=10))
    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": futuro},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "data_emprestimo não pode ser futura"


def test_us08_400_data_emprestimo_anterior_a_criacao(client, livro):
    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": "1900-01-01T10:00:00Z"},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "data_emprestimo não pode ser anterior à criação do livro"


def test_us08_404_livro_nao_existe(client):
    r = client.post(
        "/api/livros/9999/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"


def test_us08_409_emprestimo_ativo_unico(client, livro):
    payload = {"emprestado_para": "Maria", "data_emprestimo": _agora_iso()}
    client.post(f"/api/livros/{livro['id']}/emprestimos", json=payload)

    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "João", "data_emprestimo": _agora_iso()},
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "Livro já está emprestado"


# --- US09: Devolver livro ---

def test_us09_devolve_200(client, livro):
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    r = client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["data_devolucao"] is not None
    assert body["emprestado_para"] == "Maria"


def test_us09_400_sem_emprestimo_ativo(client, livro):
    r = client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "Livro não está emprestado"


def test_us09_400_data_devolucao_anterior_a_emprestimo(client, livro):
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    r = client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": "2000-01-01T10:00:00Z"},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "data_devolucao não pode ser anterior à data_emprestimo"


def test_us09_400_data_devolucao_futura(client, livro):
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    futuro = _iso(datetime.now(tz=UTC) + timedelta(days=10))
    r = client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": futuro},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "data_devolucao não pode ser futura"


def test_us09_404_livro_nao_existe(client):
    r = client.request(
        "DELETE",
        "/api/livros/9999/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"


def test_us09_pode_emprestar_de_novo_apos_devolver(client, livro):
    payload = {"emprestado_para": "Maria", "data_emprestimo": _agora_iso()}
    client.post(f"/api/livros/{livro['id']}/emprestimos", json=payload)
    client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    r = client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "João", "data_emprestimo": _agora_iso()},
    )
    assert r.status_code == 201


# --- US10: Histórico de empréstimos ---

def test_us10_lista_vazia_quando_nunca_emprestado(client, livro):
    r = client.get(f"/api/livros/{livro['id']}/emprestimos")
    assert r.status_code == 200
    assert r.json() == []


def test_us10_404_livro_nao_existe(client):
    r = client.get("/api/livros/9999/emprestimos")
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"


def test_us10_ordem_desc_por_data_emprestimo(client, livro):
    import time

    payload = {"emprestado_para": "A", "data_emprestimo": _agora_iso()}
    client.post(f"/api/livros/{livro['id']}/emprestimos", json=payload)
    client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    time.sleep(1.1)
    payload = {"emprestado_para": "B", "data_emprestimo": _agora_iso()}
    client.post(f"/api/livros/{livro['id']}/emprestimos", json=payload)
    client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    time.sleep(1.1)
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "C", "data_emprestimo": _agora_iso()},
    )

    r = client.get(f"/api/livros/{livro['id']}/emprestimos")
    nomes = [e["emprestado_para"] for e in r.json()]
    assert nomes == ["C", "B", "A"]


# --- RN07: estado emprestado é derivado nas respostas de livro ---

def test_rn07_livro_recem_criado_nao_esta_emprestado(client):
    r = client.post("/api/livros", json=LIVRO_BASE)
    body = r.json()
    assert body["emprestado"] is False
    assert body["emprestado_para"] is None
    assert body["data_emprestimo"] is None


def test_rn07_apos_emprestar_get_reflete_estado(client, livro):
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    body = client.get(f"/api/livros/{livro['id']}").json()
    assert body["emprestado"] is True
    assert body["emprestado_para"] == "Maria"
    assert body["data_emprestimo"] is not None


def test_rn07_apos_devolver_volta_a_false(client, livro):
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    body = client.get(f"/api/livros/{livro['id']}").json()
    assert body["emprestado"] is False
    assert body["emprestado_para"] is None
    assert body["data_emprestimo"] is None


# --- RN11: cascade delete ---

def test_rn11_remover_livro_apaga_emprestimos(client, livro):
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "Maria", "data_emprestimo": _agora_iso()},
    )
    client.request(
        "DELETE",
        f"/api/livros/{livro['id']}/emprestimos",
        json={"data_devolucao": _agora_iso()},
    )
    client.post(
        f"/api/livros/{livro['id']}/emprestimos",
        json={"emprestado_para": "João", "data_emprestimo": _agora_iso()},
    )
    # 2 emprestimos no historico

    r = client.delete(f"/api/livros/{livro['id']}")
    assert r.status_code == 204

    # Livro recriado nao herda emprestimos antigos
    novo = client.post("/api/livros", json=LIVRO_BASE).json()
    historico = client.get(f"/api/livros/{novo['id']}/emprestimos").json()
    assert historico == []


# --- US06 atualizada: filtros novos em GET /api/livros ---

@pytest.fixture
def biblioteca_emprestimos(client):
    """Cria 4 livros e empresta 2 deles."""
    livros = [
        {"titulo": f"L{i}", "autor": "A", "editora": "E", "ano_publicacao": 2000}
        for i in range(1, 5)
    ]
    for livro in livros:
        client.post("/api/livros", json=livro)

    agora = _agora_iso()
    client.post(
        "/api/livros/1/emprestimos",
        json={"emprestado_para": "Maria Silva", "data_emprestimo": agora},
    )
    client.post(
        "/api/livros/2/emprestimos",
        json={"emprestado_para": "João Souza", "data_emprestimo": agora},
    )
    return client


def test_us06_filtro_emprestado_true(biblioteca_emprestimos):
    r = biblioteca_emprestimos.get("/api/livros?emprestado=true")
    ids = sorted(l["id"] for l in r.json())
    assert ids == [1, 2]


def test_us06_filtro_emprestado_false(biblioteca_emprestimos):
    r = biblioteca_emprestimos.get("/api/livros?emprestado=false")
    ids = sorted(l["id"] for l in r.json())
    assert ids == [3, 4]


def test_us06_filtro_emprestado_para_parcial_case_insensitive(biblioteca_emprestimos):
    r = biblioteca_emprestimos.get("/api/livros?emprestado_para=MARIA")
    ids = [l["id"] for l in r.json()]
    assert ids == [1]


def test_us06_filtro_emprestado_para_exclui_sem_ativo(biblioteca_emprestimos):
    # 'xyz' nao bate em 'Maria Silva' nem 'Joao Souza'; livros 3/4
    # nao tem ativo, entao devem ser excluidos do resultado.
    r = biblioteca_emprestimos.get("/api/livros?emprestado_para=xyz")
    assert r.json() == []


def test_us06_filtro_emprestado_desde(biblioteca_emprestimos):
    futuro = _iso(datetime.now(tz=UTC) + timedelta(days=1))
    r = biblioteca_emprestimos.get(f"/api/livros?emprestado_desde={futuro}")
    assert r.json() == []


def test_us06_filtro_emprestado_ate(biblioteca_emprestimos):
    passado = _iso(datetime.now(tz=UTC) - timedelta(days=1))
    r = biblioteca_emprestimos.get(f"/api/livros?emprestado_ate={passado}")
    assert r.json() == []


def test_us06_filtros_combinados_emprestado_e_lido(biblioteca_emprestimos):
    biblioteca_emprestimos.patch("/api/livros/1", json={"lido": True})
    r = biblioteca_emprestimos.get("/api/livros?emprestado=true&lido=true")
    assert [l["id"] for l in r.json()] == [1]


def test_us06_400_emprestado_invalido(biblioteca_emprestimos):
    r = biblioteca_emprestimos.get("/api/livros?emprestado=sim")
    assert r.status_code == 400
    assert r.json()["detail"] == "emprestado deve ser true ou false"


def test_us06_400_data_invalida(biblioteca_emprestimos):
    r = biblioteca_emprestimos.get("/api/livros?emprestado_desde=banana")
    assert r.status_code == 400
    assert "emprestado_desde" in r.json()["detail"]
