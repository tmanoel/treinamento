import time

import pytest

LIVRO_BASE = {
    "titulo": "O Hobbit",
    "autor": "J.R.R. Tolkien",
    "editora": "HarperCollins",
    "ano_publicacao": 1937,
}


# --- Health check (RNF06) ---

def test_health_retorna_200(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- US01: Cadastrar livro ---

def test_us01_cadastra_livro_completo(client):
    r = client.post("/api/livros", json={**LIVRO_BASE, "lido": True})
    assert r.status_code == 201
    body = r.json()
    assert body["titulo"] == "O Hobbit"
    assert body["lido"] is True
    assert isinstance(body["id"], int) and body["id"] >= 1
    assert body["created_at"].endswith("Z")
    assert body["updated_at"].endswith("Z")


def test_us01_lido_omitido_vira_false(client):
    r = client.post("/api/livros", json=LIVRO_BASE)
    assert r.status_code == 201
    assert r.json()["lido"] is False


def test_us01_400_titulo_ausente(client):
    payload = {k: v for k, v in LIVRO_BASE.items() if k != "titulo"}
    r = client.post("/api/livros", json=payload)
    assert r.status_code == 400
    assert r.json()["detail"] == "titulo é obrigatório"


def test_us01_400_titulo_string_vazia(client):
    r = client.post("/api/livros", json={**LIVRO_BASE, "titulo": ""})
    assert r.status_code == 400
    assert r.json()["detail"] == "titulo é obrigatório"


def test_us01_400_titulo_so_espacos(client):
    r = client.post("/api/livros", json={**LIVRO_BASE, "titulo": "   "})
    assert r.status_code == 400
    assert r.json()["detail"] == "titulo é obrigatório"


def test_us01_400_ano_fora_intervalo(client):
    r = client.post("/api/livros", json={**LIVRO_BASE, "ano_publicacao": 2099})
    assert r.status_code == 400
    assert "ano_publicacao deve ser um número inteiro entre 1400 e" in r.json()["detail"]


def test_us01_400_ano_como_string(client):
    r = client.post("/api/livros", json={**LIVRO_BASE, "ano_publicacao": "1937"})
    assert r.status_code == 400
    assert "ano_publicacao deve ser" in r.json()["detail"]


def test_us01_409_duplicata(client):
    client.post("/api/livros", json=LIVRO_BASE)
    r = client.post("/api/livros", json=LIVRO_BASE)
    assert r.status_code == 409
    assert r.json()["detail"] == "Já existe um livro com este título e autor"


def test_us01_409_duplicata_case_insensitive(client):
    client.post("/api/livros", json=LIVRO_BASE)
    r = client.post(
        "/api/livros",
        json={**LIVRO_BASE, "titulo": "O HOBBIT", "autor": "j.r.r. tolkien"},
    )
    assert r.status_code == 409


# --- US02: Listar livros ---

def test_us02_lista_vazia(client):
    r = client.get("/api/livros")
    assert r.status_code == 200
    assert r.json() == []


def test_us02_lista_com_livros_em_ordem_de_id(client):
    client.post("/api/livros", json=LIVRO_BASE)
    client.post(
        "/api/livros",
        json={**LIVRO_BASE, "titulo": "O Senhor dos Anéis", "ano_publicacao": 1954},
    )
    r = client.get("/api/livros")
    assert r.status_code == 200
    ids = [livro["id"] for livro in r.json()]
    assert ids == sorted(ids)
    assert len(ids) == 2


# --- US03: Marcar livro como lido/não lido ---

def test_us03_marca_lido_true_atualiza_updated_at(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    time.sleep(1.1)  # created_at/updated_at têm precisão de segundos no JSON
    r = client.patch(f"/api/livros/{livro['id']}", json={"lido": True})
    assert r.status_code == 200
    body = r.json()
    assert body["lido"] is True
    assert body["updated_at"] > livro["updated_at"]
    assert body["created_at"] == livro["created_at"]


def test_us03_400_lido_nao_booleano(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.patch(f"/api/livros/{livro['id']}", json={"lido": "sim"})
    assert r.status_code == 400
    assert r.json()["detail"] == "lido deve ser true ou false"


def test_us03_404_livro_nao_existe(client):
    r = client.patch("/api/livros/9999", json={"lido": True})
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"


# --- US04: Editar livro ---

def test_us04_atualiza_multiplos_campos(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.patch(
        f"/api/livros/{livro['id']}",
        json={
            "titulo": "O Hobbit (rev)",
            "editora": "Allen & Unwin",
            "ano_publicacao": 1938,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["titulo"] == "O Hobbit (rev)"
    assert body["editora"] == "Allen & Unwin"
    assert body["ano_publicacao"] == 1938


def test_us04_404_livro_nao_existe(client):
    r = client.patch("/api/livros/9999", json={"titulo": "X"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"


def test_us04_400_body_vazio(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.patch(f"/api/livros/{livro['id']}", json={})
    assert r.status_code == 400
    assert r.json()["detail"] == "Informe ao menos um campo para atualizar"


def test_us04_400_campo_string_vazio(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.patch(f"/api/livros/{livro['id']}", json={"autor": "   "})
    assert r.status_code == 400
    assert r.json()["detail"] == "autor não pode ser vazio"


def test_us04_400_ano_invalido(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.patch(f"/api/livros/{livro['id']}", json={"ano_publicacao": 999})
    assert r.status_code == 400
    assert "ano_publicacao deve ser" in r.json()["detail"]


def test_us04_409_duplicata_com_outro_livro(client):
    client.post("/api/livros", json=LIVRO_BASE)
    outro = client.post(
        "/api/livros",
        json={**LIVRO_BASE, "titulo": "Dom Casmurro", "autor": "Machado"},
    ).json()
    r = client.patch(
        f"/api/livros/{outro['id']}",
        json={"titulo": LIVRO_BASE["titulo"], "autor": LIVRO_BASE["autor"]},
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "Já existe um livro com este título e autor"


def test_us04_reenviar_proprio_titulo_autor_nao_gera_409(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.patch(
        f"/api/livros/{livro['id']}",
        json={
            "titulo": LIVRO_BASE["titulo"],
            "autor": LIVRO_BASE["autor"],
            "editora": "Outra",
        },
    )
    assert r.status_code == 200
    assert r.json()["editora"] == "Outra"


# --- US05: Remover livro ---

def test_us05_remove_retorna_204_sem_corpo(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.delete(f"/api/livros/{livro['id']}")
    assert r.status_code == 204
    assert r.text == ""
    assert client.get(f"/api/livros/{livro['id']}").status_code == 404


def test_us05_404_livro_nao_existe(client):
    r = client.delete("/api/livros/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"


# --- US06: Buscar e filtrar ---

@pytest.fixture
def biblioteca(client):
    """Cadastra quatro livros variados para exercitar os filtros."""
    livros = [
        {"titulo": "O Hobbit", "autor": "J.R.R. Tolkien", "editora": "HarperCollins", "ano_publicacao": 1937, "lido": True},
        {"titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien", "editora": "HarperCollins", "ano_publicacao": 1954, "lido": False},
        {"titulo": "Dom Casmurro", "autor": "Machado de Assis", "editora": "Garnier", "ano_publicacao": 1899, "lido": True},
        {"titulo": "Memórias Póstumas", "autor": "Machado de Assis", "editora": "Penguin", "ano_publicacao": 1881, "lido": False},
    ]
    for livro in livros:
        client.post("/api/livros", json=livro)
    return client


def test_us06_busca_titulo_parcial_case_insensitive(biblioteca):
    r = biblioteca.get("/api/livros?titulo=hobbit")
    assert r.status_code == 200
    assert [l["titulo"] for l in r.json()] == ["O Hobbit"]


def test_us06_busca_autor_parcial_case_insensitive(biblioteca):
    r = biblioteca.get("/api/livros?autor=MACHADO")
    assert len(r.json()) == 2


def test_us06_busca_editora_parcial_case_insensitive(biblioteca):
    r = biblioteca.get("/api/livros?editora=collins")
    assert len(r.json()) == 2


def test_us06_filtro_ano_exato(biblioteca):
    r = biblioteca.get("/api/livros?ano_publicacao=1937")
    assert [l["titulo"] for l in r.json()] == ["O Hobbit"]


def test_us06_filtro_lido_true(biblioteca):
    r = biblioteca.get("/api/livros?lido=true")
    assert {l["titulo"] for l in r.json()} == {"O Hobbit", "Dom Casmurro"}


def test_us06_filtro_lido_case_insensitive(biblioteca):
    r = biblioteca.get("/api/livros?lido=FALSE")
    assert len(r.json()) == 2


def test_us06_filtros_combinados(biblioteca):
    r = biblioteca.get("/api/livros?autor=tolkien&lido=false")
    assert [l["titulo"] for l in r.json()] == ["O Senhor dos Anéis"]


def test_us06_lista_vazia_quando_nada_bate(biblioteca):
    r = biblioteca.get("/api/livros?autor=inexistente")
    assert r.status_code == 200
    assert r.json() == []


def test_us06_400_lido_invalido(biblioteca):
    r = biblioteca.get("/api/livros?lido=sim")
    assert r.status_code == 400
    assert r.json()["detail"] == "lido deve ser true ou false"


# --- US07: Consultar livro por ID ---

def test_us07_busca_por_id_200(client):
    livro = client.post("/api/livros", json=LIVRO_BASE).json()
    r = client.get(f"/api/livros/{livro['id']}")
    assert r.status_code == 200
    assert r.json()["titulo"] == LIVRO_BASE["titulo"]
    assert r.json()["id"] == livro["id"]


def test_us07_busca_por_id_404(client):
    r = client.get("/api/livros/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Livro não encontrado"
