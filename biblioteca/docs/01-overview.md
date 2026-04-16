# Biblioteca Pessoal — Overview

## O que é

Uma API para gerenciar uma biblioteca pessoal de livros. O sistema permite que o usuário cadastre, consulte e acompanhe os livros que leu ou deseja ler.

## Objetivo

Demonstrar a metodologia Spec-driven Development (SDD) na prática, onde a especificação é escrita antes do código e serve como fonte da verdade para testes e implementação.

## Contexto

O sistema é composto por:
- Uma **API REST** que gerencia os dados dos livros
- Um **frontend simples** que consome a API

## O que o sistema faz

- Permitir o cadastro de livros com título, autor e ano de publicação
- Listar todos os livros cadastrados
- Consultar um livro específico pelo ID
- Marcar um livro como lido ou não lido
- Impedir o cadastro de livros duplicados

## O que o sistema não faz (fora de escopo)

- Autenticação de usuários
- Múltiplos usuários/bibliotecas
- Integração com APIs externas de livros
