# Banco de Dados

## Tabela `links`

- `id`: UUID em formato texto
- `short_code`: identificador unico do link curto
- `original_url`: URL de destino
- `description`: descricao operacional
- `tags`: lista opcional para loja, campanha ou categoria
- `created_at`: data de criacao

## Tabela `clicks`

- `id`: UUID em formato texto
- `link_id`: referencia para `links.id`
- `timestamp`: data e hora do clique
- `ip`: IP capturado com suporte a proxy reverso
- `user_agent`: user agent bruto
- `referer`: origem HTTP quando disponivel
- `country`: pais vindo de cabecalhos de borda quando disponivel
- `device_type`: mobile ou desktop
- `source`: classificacao simplificada da origem para BI

## Escolhas

- UUID em texto para compatibilidade simples entre SQLite e PostgreSQL
- Tags em JSON para manter flexibilidade sem criar tabelas adicionais agora
- Coluna `source` adicionada para facilitar analise de origem sem depender apenas de `referer`
- Filtros de data sao aplicados em nivel de consulta para facilitar exportacao parcial e dashboards
- Cada link deve ser interpretado como origem analitica para agregacoes de unidade, campanha ou ponto de contato
