const API = "/api";

const tbody = document.querySelector("#tabela-livros tbody");
const listaVazia = document.querySelector("#lista-vazia");
const mensagem = document.querySelector("#mensagem");
const formCadastro = document.querySelector("#form-cadastro");
const formFiltros = document.querySelector("#form-filtros");
const btnLimparFiltros = document.querySelector("#btn-limpar-filtros");

let livrosAtuais = [];
let idEmEdicao = null;

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "erro" ? "mensagem-erro" : "mensagem-sucesso";
}

function limparMensagem() {
    mensagem.textContent = "";
    mensagem.className = "";
}

function filtrosAtivos() {
    const dados = new FormData(formFiltros);
    const params = new URLSearchParams();
    for (const [chave, valor] of dados.entries()) {
        if (valor !== "") params.set(chave, valor);
    }
    return params.toString();
}

async function carregarLivros() {
    const query = filtrosAtivos();
    const url = query ? `${API}/livros?${query}` : `${API}/livros`;
    const resp = await fetch(url);
    const livros = await resp.json();
    renderizarLivros(livros);
}

function renderizarLivros(livros) {
    livrosAtuais = livros;
    tbody.innerHTML = "";
    listaVazia.textContent = filtrosAtivos()
        ? "Nenhum livro encontrado."
        : "Nenhum livro cadastrado.";
    listaVazia.hidden = livros.length > 0;

    for (const livro of livros) {
        const tr = livro.id === idEmEdicao
            ? linhaEdicao(livro)
            : linhaNormal(livro);
        tbody.appendChild(tr);
    }
}

function linhaNormal(livro) {
    const tr = document.createElement("tr");
    adicionarCelula(tr, livro.titulo);
    adicionarCelula(tr, livro.autor);
    adicionarCelula(tr, livro.editora);
    adicionarCelula(tr, livro.ano_publicacao);

    const tdLido = document.createElement("td");
    const checkLido = document.createElement("input");
    checkLido.type = "checkbox";
    checkLido.checked = livro.lido;
    checkLido.setAttribute("aria-label", `Marcar "${livro.titulo}" como lido`);
    checkLido.addEventListener("change", () => alternarLido(livro, checkLido));
    tdLido.appendChild(checkLido);
    tr.appendChild(tdLido);

    const tdAcoes = document.createElement("td");
    tdAcoes.className = "acoes";
    tdAcoes.appendChild(criarBotao("Editar", () => entrarEdicao(livro.id)));
    tdAcoes.appendChild(criarBotao("Remover", () => removerLivro(livro)));
    tr.appendChild(tdAcoes);

    return tr;
}

function linhaEdicao(livro) {
    const tr = document.createElement("tr");
    tr.className = "em-edicao";

    const inputs = {};
    for (const campo of ["titulo", "autor", "editora"]) {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.type = "text";
        input.value = livro[campo];
        td.appendChild(input);
        tr.appendChild(td);
        inputs[campo] = input;
    }

    const tdAno = document.createElement("td");
    const inputAno = document.createElement("input");
    inputAno.type = "number";
    inputAno.value = livro.ano_publicacao;
    tdAno.appendChild(inputAno);
    tr.appendChild(tdAno);
    inputs.ano_publicacao = inputAno;

    const tdLido = document.createElement("td");
    const checkLido = document.createElement("input");
    checkLido.type = "checkbox";
    checkLido.checked = livro.lido;
    tdLido.appendChild(checkLido);
    tr.appendChild(tdLido);
    inputs.lido = checkLido;

    const tdAcoes = document.createElement("td");
    tdAcoes.className = "acoes";
    tdAcoes.appendChild(criarBotao("Salvar", () => salvarEdicao(livro, inputs)));
    tdAcoes.appendChild(criarBotao("Cancelar", cancelarEdicao));
    tr.appendChild(tdAcoes);

    return tr;
}

function criarBotao(texto, onClick) {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = texto;
    botao.addEventListener("click", onClick);
    return botao;
}

function adicionarCelula(tr, valor) {
    const td = document.createElement("td");
    td.textContent = valor;
    tr.appendChild(td);
}

function entrarEdicao(id) {
    idEmEdicao = id;
    limparMensagem();
    renderizarLivros(livrosAtuais);
}

function cancelarEdicao() {
    idEmEdicao = null;
    limparMensagem();
    renderizarLivros(livrosAtuais);
}

async function salvarEdicao(livro, inputs) {
    limparMensagem();

    const anoBruto = inputs.ano_publicacao.value;
    const ano = anoBruto === "" ? null : Number(anoBruto);
    const payload = {};
    if (inputs.titulo.value !== livro.titulo) payload.titulo = inputs.titulo.value;
    if (inputs.autor.value !== livro.autor) payload.autor = inputs.autor.value;
    if (inputs.editora.value !== livro.editora) payload.editora = inputs.editora.value;
    if (ano !== livro.ano_publicacao) payload.ano_publicacao = ano;
    if (inputs.lido.checked !== livro.lido) payload.lido = inputs.lido.checked;

    if (Object.keys(payload).length === 0) {
        cancelarEdicao();
        return;
    }

    const resp = await fetch(`${API}/livros/${livro.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (resp.ok) {
        const atualizado = await resp.json();
        idEmEdicao = null;
        mostrarMensagem(`"${atualizado.titulo}" atualizado.`, "sucesso");
        await carregarLivros();
        return;
    }

    const detalhe = await extrairDetalhe(resp);
    mostrarMensagem(detalhe, "erro");
}

async function alternarLido(livro, checkbox) {
    const novoValor = checkbox.checked;
    const resp = await fetch(`${API}/livros/${livro.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lido: novoValor }),
    });

    if (resp.ok) {
        livro.lido = novoValor;
        mostrarMensagem(
            `"${livro.titulo}" marcado como ${novoValor ? "lido" : "não lido"}.`,
            "sucesso",
        );
        return;
    }

    checkbox.checked = !novoValor;
    const detalhe = await extrairDetalhe(resp);
    mostrarMensagem(detalhe, "erro");
}

async function removerLivro(livro) {
    if (!confirm(`Remover "${livro.titulo}"?`)) return;

    const resp = await fetch(`${API}/livros/${livro.id}`, { method: "DELETE" });
    if (resp.status === 204) {
        mostrarMensagem(`"${livro.titulo}" removido.`, "sucesso");
        await carregarLivros();
        return;
    }

    const detalhe = await extrairDetalhe(resp);
    mostrarMensagem(detalhe, "erro");
}

async function cadastrarLivro(evento) {
    evento.preventDefault();
    limparMensagem();

    const dados = new FormData(formCadastro);
    const anoBruto = dados.get("ano_publicacao");
    const payload = {
        titulo: dados.get("titulo"),
        autor: dados.get("autor"),
        editora: dados.get("editora"),
        ano_publicacao: anoBruto === "" ? null : Number(anoBruto),
        lido: dados.get("lido") === "on",
    };

    const resp = await fetch(`${API}/livros`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (resp.status === 201) {
        const criado = await resp.json();
        mostrarMensagem(`"${criado.titulo}" cadastrado.`, "sucesso");
        formCadastro.reset();
        await carregarLivros();
        return;
    }

    const detalhe = await extrairDetalhe(resp);
    mostrarMensagem(detalhe, "erro");
}

async function aplicarFiltros(evento) {
    evento.preventDefault();
    limparMensagem();
    idEmEdicao = null;
    await carregarLivros();
}

async function limparFiltros() {
    formFiltros.reset();
    limparMensagem();
    idEmEdicao = null;
    await carregarLivros();
}

async function extrairDetalhe(resp) {
    try {
        const corpo = await resp.json();
        return corpo.detail || `Erro ${resp.status}`;
    } catch {
        return `Erro ${resp.status}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    limparMensagem();
    formCadastro.addEventListener("submit", cadastrarLivro);
    formFiltros.addEventListener("submit", aplicarFiltros);
    btnLimparFiltros.addEventListener("click", limparFiltros);
    carregarLivros();
});
