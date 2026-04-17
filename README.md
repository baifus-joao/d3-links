# D3 Links

Sistema de encurtador de links inteligente com analytics para lojas, campanhas, SAC e QR Codes.

## Stack

- Backend: FastAPI + SQLAlchemy
- Banco: SQLite em desenvolvimento, PostgreSQL em produção
- Frontend: HTML, CSS e JavaScript puros
- Deploy: Render

## Estrutura

```text
backend/
  app/
frontend/
obsidian-brain/
  D3-Links-Brain/
```

## Como rodar localmente

1. Crie um ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Ajuste o `.env` com base no `.env.example`.
4. Inicie a aplicacao:

```bash
uvicorn backend.app.main:app --reload
```

5. Acesse:

- Dashboard: `http://localhost:8000`
- Dashboard direto: `http://localhost:8000/dashboard/`
- Info da API: `http://localhost:8000/api-info`
- Swagger: `http://localhost:8000/docs`

## Principais recursos

- Criacao de links curtos customizados
- Redirecionamento com tracking de clique
- Dashboard operacional com ranking de unidades e campanhas
- Visao global de tendencia e engajamento por periodo
- Analytics por link com filtros de data
- Exportacao CSV para BI
- Geracao de QR Code por link

## Cofre Obsidian

Toda decisao tecnica do projeto fica em `obsidian-brain/D3-Links-Brain`.
