# Arquitetura

## Visao Geral

O sistema foi estruturado para separar responsabilidade por camada sem adicionar complexidade desnecessaria.

## Camadas

- `routers`: entrada HTTP e serializacao de resposta
- `services`: regras de negocio e orquestracao
- `repositories`: acesso e agregacao de dados
- `models`: entidades ORM
- `schemas`: contratos de entrada e saida
- `database`: engine, sessoes e bootstrap do banco
- `utils`: funcoes auxiliares de tracking e QR Code

## Diretrizes

- Priorizar funcionamento real antes de sofisticacao
- Preparar consultas para analytics e exportacao BI
- Manter o endpoint `/{short_code}` como nucleo de negocio
- Evitar acoplamento entre dashboard e logica da API

## Implementacao Atual

- `LinkService` concentra criacao, serializacao e recuperacao de links
- `TrackingService` resolve o short code e grava o clique antes do redirect
- `AnalyticsService` entrega agregacoes de dashboard, exportacao CSV e QR Code
- `AnalyticsService` agora tambem entrega uma visao global para o dashboard principal com top links, tendencia e distribuicao por origem
- O frontend consome a mesma API e nao depende de framework JS para manter simplicidade operacional
- O dashboard foi reorganizado em formato SaaS corporativo com topbar, rail lateral, cards de KPI, ranking operacional e drill-down individual
