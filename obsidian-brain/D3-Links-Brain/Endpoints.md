# Endpoints

## API Base

- `GET /`
- `GET /api-info`
- `GET /health`

## Analytics

- `GET /analytics/overview`

## Links

- `POST /links`
- `GET /links`
- `GET /links/{id}`
- `GET /links/{id}/stats`
- `GET /links/{id}/clicks/export`
- `GET /links/{id}/qr-code`

## Redirecionamento

- `GET /{short_code}`

## Observacoes

- `GET /` redireciona para o dashboard quando o frontend estiver presente
- O dashboard web sera servido em `GET /dashboard/`
- As informacoes institucionais da API ficam em `GET /api-info`
- O endpoint de exportacao CSV sera pensado para consumo por BI e planilhas
- `GET /analytics/overview` entrega ranking, tendencia diaria, distribuicao por origem, distribuicao por dispositivo e feed recente
- `GET /links/{id}/stats` e `GET /links/{id}/clicks/export` aceitam `start_date` e `end_date`
- O retorno de stats inclui total, serie diaria, distribuicao por dispositivo, distribuicao por origem e ultimos acessos
