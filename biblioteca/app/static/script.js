const API = "/api";

const tbody = document.querySelector("#tabela-livros tbody");
const listaVazia = document.querySelector("#lista-vazia");
const mensagem = document.querySelector("#mensagem");

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "erro" ? "mensagem-erro" : "mensagem-sucesso";
}

function limparMensagem() {
    mensagem.textContent = "";
    mensagem.className = "";
}

async function carregarLivros() {
    const resp = await fetch(`${API}/livros`);
    const livros = await resp.json();
    renderizarLivros(livros);
}

function renderizarLivros(livros) {
    tbody.innerHTML = "";
    listaVazia.hidden = livros.length > 0;

    for (const livro of livros) {
        const tr = document.createElement("tr");
        adicionarCelula(tr, livro.titulo);
        adicionarCelula(tr, livro.autor);
        adicionarCelula(tr, livro.editora);
        adicionarCelula(tr, livro.ano_publicacao);
        adicionarCelula(tr, livro.lido ? "Sim" : "Não");

        const tdAcoes = document.createElement("td");
        const btnRemover = document.createElement("button");
        btnRemover.textContent = "Remover";
        btnRemover.addEventListener("click", () => removerLivro(livro));
        tdAcoes.appendChild(btnRemover);
        tr.appendChild(tdAcoes);

        tbody.appendChild(tr);
    }
}

function adicionarCelula(tr, valor) {
    const td = document.createElement("td");
    td.textContent = valor;
    tr.appendChild(td);
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
    carregarLivros();
});
