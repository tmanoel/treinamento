const API = "/api";

const tbody = document.querySelector("#tabela-livros tbody");
const listaVazia = document.querySelector("#lista-vazia");
const mensagem = document.querySelector("#mensagem");
const formCadastro = document.querySelector("#form-cadastro");
const formFiltros = document.querySelector("#form-filtros");
const btnLimparFiltros = document.querySelector("#btn-limpar-filtros");

const dialogEmprestar = document.querySelector("#dialog-emprestar");
const dialogDevolver = document.querySelector("#dialog-devolver");
const dialogHistorico = document.querySelector("#dialog-historico");
const formEmprestar = document.querySelector("#form-emprestar");
const formDevolver = document.querySelector("#form-devolver");
const tbodyHistorico = document.querySelector("#tabela-historico tbody");
const historicoVazio = document.querySelector("#historico-vazio");

let livrosAtuais = [];
let idEmEdicao = null;
let livroEmAcao = null;

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "erro" ? "mensagem-erro" : "mensagem-sucesso";
}

function limparMensagem() {
    mensagem.textContent = "";
    mensagem.className = "";
}

const FILTROS_DATA = new Set(["emprestado_desde", "emprestado_ate"]);

function filtrosAtivos() {
    const dados = new FormData(formFiltros);
    const params = new URLSearchParams();
    for (const [chave, valor] of dados.entries()) {
        if (valor === "") continue;
        params.set(chave, FILTROS_DATA.has(chave) ? localParaUTC(valor) : valor);
    }
    return params.toString();
}

function localParaUTC(valorLocal) {
    const dt = new Date(valorLocal);
    if (Number.isNaN(dt.getTime())) return valorLocal;
    return dt.toISOString().replace(/\.\d{3}Z$/, "Z");
}

function agoraLocal() {
    const dt = new Date();
    const offset = dt.getTimezoneOffset() * 60000;
    return new Date(dt.getTime() - offset).toISOString().slice(0, 16);
}

function formatarDataUTC(iso) {
    if (!iso) return "";
    const dt = new Date(iso);
    if (Number.isNaN(dt.getTime())) return iso;
    return dt.toLocaleString("pt-BR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
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

    const tdEmprestimo = document.createElement("td");
    tdEmprestimo.textContent = livro.emprestado
        ? `${livro.emprestado_para} desde ${formatarDataUTC(livro.data_emprestimo)}`
        : "—";
    tr.appendChild(tdEmprestimo);

    const tdAcoes = document.createElement("td");
    tdAcoes.className = "acoes";
    tdAcoes.appendChild(criarBotao("Editar", () => entrarEdicao(livro.id)));
    tdAcoes.appendChild(
        livro.emprestado
            ? criarBotao("Devolver", () => abrirDialogDevolver(livro))
            : criarBotao("Emprestar", () => abrirDialogEmprestar(livro))
    );
    tdAcoes.appendChild(criarBotao("Histórico", () => abrirDialogHistorico(livro)));
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

    const tdEmprestimo = document.createElement("td");
    tdEmprestimo.textContent = livro.emprestado
        ? `${livro.emprestado_para} desde ${formatarDataUTC(livro.data_emprestimo)}`
        : "—";
    tr.appendChild(tdEmprestimo);

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

function abrirDialogEmprestar(livro) {
    livroEmAcao = livro;
    document.querySelector("#emprestar-titulo-livro").textContent = `"${livro.titulo}"`;
    document.querySelector("#emprestar-para").value = "";
    document.querySelector("#emprestar-data").value = agoraLocal();
    dialogEmprestar.showModal();
}

function abrirDialogDevolver(livro) {
    livroEmAcao = livro;
    document.querySelector("#devolver-titulo-livro").textContent =
        `"${livro.titulo}" emprestado para ${livro.emprestado_para}`;
    document.querySelector("#devolver-data").value = agoraLocal();
    dialogDevolver.showModal();
}

async function abrirDialogHistorico(livro) {
    livroEmAcao = livro;
    document.querySelector("#historico-titulo-livro").textContent = `"${livro.titulo}"`;
    tbodyHistorico.innerHTML = "";
    historicoVazio.hidden = true;
    dialogHistorico.showModal();

    const resp = await fetch(`${API}/livros/${livro.id}/emprestimos`);
    if (!resp.ok) {
        const detalhe = await extrairDetalhe(resp);
        mostrarMensagem(detalhe, "erro");
        dialogHistorico.close();
        return;
    }

    const emprestimos = await resp.json();
    historicoVazio.hidden = emprestimos.length > 0;
    for (const emp of emprestimos) {
        const tr = document.createElement("tr");
        adicionarCelula(tr, emp.emprestado_para);
        adicionarCelula(tr, formatarDataUTC(emp.data_emprestimo));
        adicionarCelula(tr, emp.data_devolucao ? formatarDataUTC(emp.data_devolucao) : "—");
        tbodyHistorico.appendChild(tr);
    }
}

async function confirmarEmprestimo(evento) {
    if (!livroEmAcao) return;
    evento.preventDefault();
    limparMensagem();

    const dados = new FormData(formEmprestar);
    const payload = {
        emprestado_para: dados.get("emprestado_para"),
        data_emprestimo: localParaUTC(dados.get("data_emprestimo")),
    };

    const resp = await fetch(`${API}/livros/${livroEmAcao.id}/emprestimos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (resp.status === 201) {
        mostrarMensagem(
            `"${livroEmAcao.titulo}" emprestado para ${payload.emprestado_para}.`,
            "sucesso",
        );
        dialogEmprestar.close();
        livroEmAcao = null;
        await carregarLivros();
        return;
    }

    const detalhe = await extrairDetalhe(resp);
    mostrarMensagem(detalhe, "erro");
}

async function confirmarDevolucao(evento) {
    if (!livroEmAcao) return;
    evento.preventDefault();
    limparMensagem();

    const dados = new FormData(formDevolver);
    const payload = { data_devolucao: localParaUTC(dados.get("data_devolucao")) };

    const resp = await fetch(`${API}/livros/${livroEmAcao.id}/emprestimos`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (resp.ok) {
        mostrarMensagem(`"${livroEmAcao.titulo}" devolvido.`, "sucesso");
        dialogDevolver.close();
        livroEmAcao = null;
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
    formCadastro.addEventListener("submit", cadastrarLivro);
    formFiltros.addEventListener("submit", aplicarFiltros);
    btnLimparFiltros.addEventListener("click", limparFiltros);
    formEmprestar.addEventListener("submit", confirmarEmprestimo);
    formDevolver.addEventListener("submit", confirmarDevolucao);
    document.querySelectorAll("[data-fechar-dialog]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const dlg = document.querySelector(`#${btn.dataset.fecharDialog}`);
            if (dlg) dlg.close();
        });
    });
    carregarLivros();
});
