# D3 Links Brain

## Status Atual

- Projeto iniciado em 2026-04-16
- Backend funcional com redirecionamento, tracking, criacao de links, stats, CSV e QR Code
- Visao global de analytics adicionada para sustentar o dashboard operacional
- Dashboard web reposicionado como painel de inteligencia operacional servido pelo FastAPI em `/dashboard`
- Validacao local concluida para criacao, redirecionamento, analytics, exportacao e QR

## Guias do Cofre

- [[Arquitetura]]
- [[Endpoints]]
- [[Banco-de-Dados]]
- [[Melhorias-Futuras]]

## Decisoes iniciais

- FastAPI como API principal
- SQLAlchemy 2 como camada ORM
- SQLite em desenvolvimento e PostgreSQL em producao via `DATABASE_URL`
- Dashboard servido pelo proprio FastAPI em `/dashboard`
- Documentacao viva mantida durante a construcao

## Entrega atual

- O endpoint `/{short_code}` registra IP, user agent, referer, pais por header e tipo de dispositivo antes do redirecionamento
- Os endpoints de analytics aceitam filtro por `start_date` e `end_date`
- O painel passa a tratar cada link como entidade analitica com ranking e comparacao por periodo
- A home agora prioriza leitura executiva: lideres, tendencia, canais, feed recente e drill-down por origem
- A camada atual esta pronta para evoluir para autenticacao leve, jobs assincronos e BI mais pesado
- A raiz da aplicacao (`/`) agora direciona o usuario direto para o dashboard
