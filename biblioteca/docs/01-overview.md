# Biblioteca Pessoal — Overview

## O que é

Uma API para gerenciar uma biblioteca pessoal de livros. O sistema permite que o usuário cadastre, consulte e acompanhe os livros que leu ou deseja ler.

## Objetivo
Centralizar em um único lugar o cadastro de livros que o usuário possui ou deseja ler, evitando listas dispersas em anotações, planilhas ou aplicativos diversos.

## Contexto

O sistema é composto por:
- Uma **API REST** que gerencia os dados dos livros
- Um **frontend simples** (HTML + JavaScript puro) para testar a API pelo navegador

## O que o sistema faz

- Permitir o cadastro de livros com título, autor, editora e ano de publicação
- Permitir editar o cadastro de livros
- Permitir remover o cadastro de livros
- Filtrar livros por título, autor, editora, status leitura e ano de publicação
- Listar todos os livros cadastrados
- Marcar um livro como lido ou não lido
- Impedir o cadastro de livros duplicados
- Consultar livro por ID

## O que o sistema não faz (fora de escopo - Talvez fará numa fase II)

- Autenticação de usuários
- Múltiplos usuários/bibliotecas
- Integração com APIs externas de livros
