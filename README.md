# DailyFlow

Organizador pessoal de rotina: tarefas, hábitos, calendário, metas, relatórios,
gamificação e lembretes automáticos via bot do Telegram.

> Em desenvolvimento incremental por fases — veja o status de cada módulo abaixo.

## Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL (arquitetura em camadas
  `controllers → services → repositories → models`)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + TanStack Query
- **Bot**: python-telegram-bot + APScheduler (serviço separado, Fase 3)
- **Infra**: Docker Compose (Postgres + backend + frontend [+ bot])

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose (recomendado), **ou**
- Python 3.12+, Node.js 22+ e PostgreSQL 16 instalados localmente

## Como rodar com Docker (recomendado)

1. Copie o arquivo de variáveis de ambiente de exemplo:

   ```bash
   cp .env.example .env
   ```

   Ajuste os valores se quiser (ao menos troque `SECRET_KEY` antes de ir para produção).

2. Suba a stack:

   ```bash
   docker compose up --build
   ```

   Isso inicia três serviços:
   - `postgres` — banco de dados (porta `5432`)
   - `backend` — API FastAPI em `http://localhost:8000` (aplica as migrações do
     Alembic automaticamente ao iniciar)
   - `frontend` — Vite dev server em `http://localhost:5173`

3. Acesse `http://localhost:5173`, crie uma conta e explore.

4. Para parar tudo: `docker compose down` (adicione `-v` para também apagar o volume
   do banco de dados).

## Como rodar localmente (sem Docker)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example ../.env   # ou crie backend/.env com DATABASE_URL apontando para o seu Postgres local
alembic upgrade head
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000` (documentação interativa em `/docs`).

Rodar os testes:

```bash
pytest
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # ajuste VITE_API_URL se necessário
npm run dev
```

A aplicação sobe em `http://localhost:5173`.

Rodar os testes:

```bash
npm test
```

> **Nota (Node 22+/Linux)**: o script `npm test` já inclui `NODE_OPTIONS=--no-webstorage`,
> necessário porque o `localStorage` global nativo do Node conflita com o do jsdom
> usado pelo Vitest nos testes de componentes.

## Variáveis de ambiente

Veja [`.env.example`](.env.example) para a lista completa e comentada. As principais:

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | String de conexão do PostgreSQL usada pelo backend |
| `SECRET_KEY` | Chave usada para assinar tokens JWT — **gere uma nova em produção** |
| `CORS_ORIGINS` | Lista JSON de origens permitidas pela API |
| `SMTP_*` | Configuração de envio de e-mail (recuperação de senha). Sem isso, o link é apenas logado no console em dev |
| `TELEGRAM_BOT_TOKEN` | Token do bot gerado via [@BotFather](https://t.me/BotFather) — necessário a partir da Fase 3 |
| `VITE_API_URL` | URL base da API consumida pelo frontend |

## Guia de deploy em produção

Os arquivos do repositório (Dockerfiles e `docker-compose.yml`) são voltados para
**desenvolvimento** (hot-reload no backend e no Vite). Em produção, ajuste os pontos
abaixo — a arquitetura recomendada é: Postgres gerenciado (ou em container com volume
persistente e backups), API FastAPI atrás de um proxy reverso com HTTPS, frontend
publicado como build estático, e o bot do Telegram como serviço de longa duração
(worker), todos compartilhando o mesmo banco.

### 1. Variáveis de ambiente

Crie um `.env` de produção (nunca reaproveite o `.env.example` nem o `.env` de
desenvolvimento) e ajuste, no mínimo:

- `SECRET_KEY` — gere um valor longo e aleatório, por exemplo com
  `python -c "import secrets; print(secrets.token_urlsafe(64))"`. Nunca reutilize a
  chave de desenvolvimento nem a deixe em texto plano em repositórios.
- `ENVIRONMENT=production` e `DEBUG=false` — desativa detalhes de erro/stack traces
  nas respostas da API.
- `DATABASE_URL` — string de conexão do Postgres de produção (gerenciado ou próprio),
  de preferência com usuário com privilégios mínimos necessários.
- `CORS_ORIGINS` — lista JSON **apenas** com o(s) domínio(s) reais do frontend
  (ex.: `["https://app.seudominio.com"]`); nunca use `*` nem inclua `localhost`.
- `FRONTEND_URL` — URL pública do frontend, usada nos links enviados por e-mail
  (recuperação de senha).
- `SMTP_*` — credenciais de um provedor SMTP real (ex.: SES, SendGrid, Mailgun);
  sem isso, o link de recuperação de senha só é logado no console, o que é
  inaceitável em produção.
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_BOT_USERNAME` — token gerado via
  [@BotFather](https://t.me/BotFather) (veja a seção de segurança abaixo sobre como
  protegê-lo).
- `VITE_API_URL` — URL pública da API (ex.: `https://api.seudominio.com/api`).
  **Atenção**: variáveis `VITE_*` são embutidas no bundle durante o `npm run build`,
  então defina-a antes de gerar o build de produção do frontend (não é algo que possa
  ser trocado em runtime depois de publicado).

### 2. Migrações do banco de dados

Antes de iniciar (ou atualizar) a API em produção, aplique as migrações do Alembic:

```bash
cd backend
alembic upgrade head
```

O `Dockerfile` do backend já roda `alembic upgrade head` automaticamente antes de
subir o `uvicorn` (veja o `CMD`), então isso acontece a cada novo deploy do container.
Se preferir mais controle (ex.: rodar migrações em uma etapa separada do pipeline de
CI/CD antes de trocar a versão da API), rode o comando acima manualmente como um passo
prévio do deploy.

### 3. Build do frontend

Para produção, gere os arquivos estáticos otimizados em vez de rodar o servidor de
desenvolvimento do Vite:

```bash
cd frontend
npm install
VITE_API_URL=https://api.seudominio.com/api npm run build
```

Isso cria a pasta `dist/` com HTML/CSS/JS minificados e versionados por hash. Publique
o conteúdo de `dist/` em qualquer servidor de arquivos estáticos com suporte a SPA
(fallback de rotas para `index.html`) — por exemplo Nginx, Caddy, Vercel, Netlify ou um
bucket com CDN. Não use `npm run dev`/`vite preview` em produção.

### 4. Backend em produção

- Rode a API atrás de um **proxy reverso com HTTPS** (Nginx, Caddy, Traefik, ou o
  load balancer do seu provedor de nuvem) — nunca exponha o `uvicorn` diretamente
  à internet sem TLS.
- Para aproveitar múltiplos núcleos, rode com mais de um worker, por exemplo:
  `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4` (ajuste conforme a
  CPU disponível).
- Garanta que `postgres` use um volume persistente com backups regulares — perder o
  banco significa perder contas, tarefas, hábitos, histórico e XP de todos os usuários.
- O `telegram-bot` deve rodar como um processo de longa duração (worker) sempre ativo,
  já que mantém o `AsyncIOScheduler` que dispara os lembretes periódicos.

### 5. Considerações de segurança

- **HTTPS obrigatório** em todos os domínios públicos (API e frontend) — tokens JWT e
  senhas trafegam nessas conexões.
- **Nunca** commite `.env`, tokens ou chaves no repositório — todos os arquivos
  sensíveis já estão listados no `.gitignore`. Trate `SECRET_KEY` e
  `TELEGRAM_BOT_TOKEN` como segredos: armazene-os em um cofre de segredos do seu
  provedor (ex.: variáveis de ambiente do serviço, AWS Secrets Manager, etc.) e nunca
  os cole em logs, mensagens, issues ou documentação.
- Restrinja `CORS_ORIGINS` ao(s) domínio(s) reais do frontend — uma configuração
  permissiva permite que sites maliciosos façam requisições autenticadas em nome dos
  seus usuários.
- Configure SMTP real para o fluxo de recuperação de senha; em produção, depender do
  fallback "loga no console" deixa essa funcionalidade quebrada para os usuários.
- Gere uma `SECRET_KEY` nova e exclusiva para produção — reutilizar a de
  desenvolvimento permite forjar tokens JWT válidos.
- Avalie reduzir `ACCESS_TOKEN_EXPIRE_MINUTES`/`REFRESH_TOKEN_EXPIRE_DAYS` conforme a
  política de segurança desejada, e tenha um plano para revogar refresh tokens
  comprometidos.

## Status do desenvolvimento

- [x] **Fase 1** — Fundação + Autenticação (cadastro, login, recuperação de senha,
      perfil, tema claro/escuro, layout base, Docker Compose)
- [x] **Fase 2** — Tarefas, Hábitos e Dashboard
- [x] **Fase 3** — Integração com bot do Telegram (lembretes automáticos)
- [x] **Fase 4** — Calendário (mês, com arrastar e soltar de tarefas), Metas
      (CRUD com cálculo de progresso) e Gamificação (XP, níveis, conquistas e medalhas)
- [x] **Fase 5** — Relatórios de produtividade (diário/semanal/mensal com gráficos),
      exportação em PDF e Excel, revisão de responsividade/tema e guia de deploy
      em produção

## Estrutura do projeto

```
DailyFlow/
├── backend/          # API FastAPI (controllers/services/repositories/models)
├── frontend/         # SPA React + TypeScript + Vite
├── telegram-bot/     # Bot de lembretes (a partir da Fase 3)
├── docker-compose.yml
└── .env.example
```
