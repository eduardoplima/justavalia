# Progresso — Justavalia

Documento vivo, atualizado ao fim de cada fase. O detalhe de fases concluídas migra para
`docs/ROADMAP.md`; este arquivo mantém o panorama e as decisões.

## Panorama das fases

| Fase | Descrição | Status |
|---|---|---|
| 0 | Fundação (skeleton, compose, CI, subagentes) | ✅ Concluída |
| 1 | Identidade → tema Tailwind | ✅ Concluída |
| 2 | Site público | ✅ Concluída |
| 3 | Pedido + pagamento (mock) | ✅ Concluída |
| 4 | Upload resumível + protocolo guiado | ⬜ Pendente |
| 5 | Pipeline de processamento | ⬜ Pendente |
| 6 | Triagem + rascunho PTAM + PDF | ⬜ Pendente |
| 7 | Dashboard de revisão + assinatura | ⬜ Pendente |
| 8 | Entrega + notificações | ⬜ Pendente |
| 9 | LGPD + hardening + deploy | ⬜ Pendente |

## Fase 0 — checklist

- [x] Repo Python + `pyproject.toml` (uv, PEP 621) + `uv.lock`
- [x] Skeleton Django: pacote `justavalia/` com os 11 apps (core + 10)
- [x] Settings split `base/dev/prod/test`
- [x] Usuário customizado `core.User` + migração inicial
- [x] Wiring do Celery (`celery -A justavalia`) + filas `media,docs,ia,notify`
- [x] Endpoints de saúde `/healthz/` e `/readyz/`
- [x] Docker Compose (web, worker, beat, redis, postgres, minio, createbuckets)
- [x] Dockerfile único (ffmpeg baked) + entrypoint (migrate só no web)
- [x] Makefile (`up`, `test`, `lint`, `worker`, `shell`, `seed`, `styleguide`, …)
- [x] CI GitHub Actions (ruff + pytest + checagem de migrações)
- [x] pre-commit (ruff, ruff-format, detect-private-key, large-files)
- [x] `.env.example` completo
- [x] 4 subagentes em `.claude/agents/`
- [x] `docs/PROGRESSO.md`
- [x] Aceite: `make up` sobe tudo; `make test` verde (**8 passed**) — validado 2026-07-05

> Revisor de fim de fase: **APROVADO** (sem bloqueadores). Melhorias registradas p/ fases 1 e 9:
> `*.zip` no `.gitignore` (feito), `SECRET_KEY` sem default em prod (F9), `STORAGES` prod com
> `OPTIONS` (F9), `worker/beat` aguardarem migrações quando tocarem o ORM (F5).

## Fase 1 — checklist

- [x] `design/` descompactado e inventariado; assets de marca em `justavalia/static/img/`
- [x] `design/tokens.md` extraído (cores, tipografia, espaçamento, componentes)
- [x] Tema Tailwind v4 a partir dos tokens (`justavalia/static/src/input.css`, `@theme` + componentes)
- [x] `templates/` base + partials (header sticky, footer tinta, FAB WhatsApp) com HTMX/Alpine
- [x] Styleguide interno `/styleguide/` (gated por `SHOW_STYLEGUIDE=default DEBUG`) renderizando
      todos os tokens e componentes — **validado em navegador (Playwright)**
- [x] Alvos `make css`/`css-watch`/`styleguide`; build de css no Dockerfile
- [x] Teste `tests/test_styleguide.py` (200 ligado / 404 desligado) — suíte: **10 passed**

### Decisões (Fase 1)

- **Toolchain de CSS: Tailwind v4 standalone via `pytailwindcss`** (dev dep, gerenciado pelo uv,
  **sem Node**) — atende ao guardrail "sem SPA build". `app.css` é build-artifact (gitignore +
  build no Dockerfile + `make css` no host, bind-mounted em dev).
- Tokens `--jv-*` mapeados para o `@theme` do Tailwind → utilidades da marca (`bg-tinta`,
  `text-cobre`, `p-section`, `max-w-largo`…) e componentes `.jv-*`.
- Breakpoint mobile do header usa `md:` (768px) do Tailwind (≈ os ~720px do protótipo).
- Styleguide gated por `SHOW_STYLEGUIDE` (default = DEBUG) — não vaza em produção.
- Correção de fundação capturada: `STATICFILES_DIRS` apontava para `BASE_DIR/static`
  (inexistente); ajustado para `BASE_DIR/justavalia/static`.

## Fase 2 — checklist

- [x] Roteamento das 7 páginas (`site_publico/urls.py`, TemplateView) + nav ativa (partial `_navlink`)
- [x] Home, Como funciona, Para advogados, Quem assina, FAQ (cópia literal dos `design_reference`)
- [x] Privacidade e Termos (esqueleto com `[PLACEHOLDER]` jurídico; escopo respeita guardrail #3)
- [x] Header/footer com links reais (`{% url %}`); CTA → WhatsApp; placeholders de Go-Live preservados
- [x] Testes de rota/nav/`<h1>` único (`tests/test_site_publico.py`); suíte **26 passed**
- [x] **Aceite: Lighthouse mobile ≥ 90** em todas as 7 páginas (perf 93–95, a11y 95–96) — medido

### Decisões (Fase 2)

- **Páginas construídas em paralelo** por subagentes dev-frontend (um por página), integradas pelo
  orquestrador; Privacidade/Termos escritas pelo orquestrador.
- **Fontes auto-hospedadas** (`justavalia/static/fonts/`, latin + latin-ext woff2 + `@font-face`
  no tema) no lugar do Google Fonts CDN — derrubou FCP de 2.6 s → 1.2 s e foi o que levou a
  performance de 87 → 94. Preload dos subsets latinos no `base.html`.
- **`GZipMiddleware`** ligado (compressão de texto).
- Favicon = monograma SVG.
- URL slugs em pt-BR (`/como-funciona/`, `/para-advogados/`, `/quem-assina/`, `/faq/`,
  `/privacidade/`, `/termos/`).

## Fase 3 — checklist

- [x] Máquina de estados própria (`pedidos/state_machine.py`): enum + tabela de transições +
      `validar_transicao`; **cobertura exaustiva** (matriz 12×12 — toda transição proibida falha)
- [x] Modelo `Pedido` + `TransicaoLog` **imutável** (append-only, ator/timestamp/payload)
- [x] Regra inviolável: `APPROVED_FOR_SIGNATURE → SIGNED` só com ação humana autenticada
      (`ator` persistido + `por_humano=True`); recusa task/cron/webhook/IA — **testado**
- [x] Adapter `pagamentos/` (interface `PixProvider` + `MockPix`) trocável por `PIX_PROVIDER`
- [x] `Pagamento` model + serviço `iniciar_pagamento`/`confirmar_pagamento` (transições atômicas)
- [x] Fluxo público: form de pedido → pagamento (PIX mock) → página de status com timeline
- [x] Admin (Pedido + timeline inline read-only, TransicaoLog imutável, Pagamento)
- [x] **Aceite:** pedido navega DRAFT → AWAITING_UPLOAD via mock, timeline auditada —
      **validado em navegador** (Playwright) e por teste de integração; suíte **205 passed**

### Decisões (Fase 3)

- **Máquina de estados = módulo crítico, implementada pelo orquestrador** (não delegada),
  por TDD. Camada pura (`state_machine.py`) decide o permitido; o modelo grava estado + log
  atômico e aplica o guard humano do SIGNED.
- **Log de transição imutável**: `save()` recusa update, `delete()` bloqueado (trilha de
  auditoria). Admin do log é read-only.
- **Pagamento atrás de adapter** (`PixProvider`) com `MockPix` em dev; registro de provedores
  em `pagamentos/service.py` pronto para Mercado Pago/Efí (troca por `PIX_PROVIDER`).
- Transições causadas pelo pagamento são atribuídas a `pagamento:<provedor>` no log.
- Dados do cliente mínimos (LGPD) nesta fase; ampliam nas fases seguintes.

### Revisor Fase 3 — APROVADO (sem bloqueadores). Aplicado + pendências:

- **Aplicado agora:** M2 — `transicionar` trava a linha (`select_for_update`) e revalida sob
  o lock (evita dupla transição/assinatura concorrente). M3 — `get_pix_provider` recusa
  `mock` com `DEBUG=False` (MockPix nunca em produção), com teste.
- **Pendências rastreadas:** M1 — imutabilidade do log é a nível de app; antes do go-live,
  trigger no PostgreSQL contra `UPDATE/DELETE` por queryset (**Fase 9**). M4 — registro de
  consentimento LGPD (timestamp+IP+versão do termo) na coleta de PII (**Fase 4/9**). M5 — na
  integração PIX real, aprovação deve vir de **webhook** do provedor, não de POST do cliente
  (**quando entrar o provedor real**).

## Registro de decisões (Fase 0)

- **Packaging: uv.** Binário único, resolves rápidos, `pyproject.toml` PEP 621, `uv.lock`
  reprodutível, pin de Python 3.12 (`.python-version`). Host roda 3.14; tudo executa na
  imagem 3.12.
- **Settings split** `base/dev/prod/test`: fronteira de segurança dev↔prod; `test` com Celery
  ansioso, hasher rápido, e-mail em memória.
- **django-environ** para leitura tipada de env (`env.bool/list/db()`).
- **Custom User já na Fase 0** (`core.User`) — evita o retrabalho de trocar `AUTH_USER_MODEL`
  após a primeira migração.
- **Auditoria adiada para a Fase 3**: o log imutável real é o de transições da máquina de
  estados do `Pedido`; não criamos tabela ociosa agora.
- **Deps de fases futuras adiadas** (WeasyPrint→F6, pyHanko→F7, anthropic→F5/6, sentry/flower
  →F9) — declaradas em `[project.optional-dependencies]` mas não instaladas. **Exceção:** o
  binário `ffmpeg` já entra na imagem (apt estável, evita rebuild na F5). `psycopg[binary]`
  para dispensar compilador/libpq-dev na imagem dev (revisão para prod na F9).
- **Migrações aplicadas só pelo serviço web** (via `RUN_MIGRATIONS=1` no entrypoint) — evita
  corrida entre web/worker/beat.

## Registro de ambiente / modelo do orquestrador

O CLAUDE.md especifica **Claude Fable 5** como sessão principal (orquestrador). Fable 5 não
está disponível neste plano; conforme instrução do próprio CLAUDE.md ("se indisponível no
plano, usar o Opus mais recente e registrar em docs/PROGRESSO.md"), o orquestrador está
rodando em **Claude Opus 4.8** (`claude-opus-4-8`, janela de contexto de 1M). Data do
registro: 2026-07-05.

Nota: isto é distinto de `ANTHROPIC_MODEL` (o modelo da API usado pelo pipeline de IA), que
permanece um placeholder vazio até a Fase 5/6, a ser fixado consultando docs.claude.com.
