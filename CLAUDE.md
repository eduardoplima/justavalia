# CLAUDE.md — Justavalia

## O que é este projeto

Justavalia é um serviço de avaliação de imóveis 100% remoto. O cliente paga um preço fixo (R$ 299, residencial urbano), envia documentos, fotos e vídeo do imóvel por um protocolo guiado; o sistema processa as mídias, gera um rascunho de PTAM (Parecer Técnico de Avaliação Mercadológica) com apoio da API da Anthropic; um avaliador humano (Eduardo, CRECI + CNAI) revisa, aprova e assina digitalmente com certificado ICP-Brasil em nuvem; o PDF assinado é entregue em até 5 dias úteis.

**Regra de ouro do produto: a IA elabora, o humano assina. Nenhum documento é assinado sem ação humana explícita.**

## Definition of Done (estado-alvo deste repositório)

Fluxo E2E demonstrável em staging (Docker Compose): pedido → pagamento (mock) → upload resumível de fotos/vídeo/documentos → pipeline de processamento → rascunho de PTAM → dashboard de revisão → aprovação humana → assinatura PAdES (MockSigner com certificado de teste em dev) → PDF entregue por link seguro + notificação (mock).

Integrações reais (ICP, PIX, WhatsApp) ficam atrás de adapters, prontas para receber credenciais. O **Checklist de Go-Live** (final deste arquivo) lista o que só o Eduardo pode fornecer.

## Decisões em aberto — NÃO bloqueiam o início, bloqueiam fases específicas

| Decisão | Bloqueia | Status |
|---|---|---|
| Provedor de assinatura ICP-Brasil em nuvem (candidatos a verificar: BirdID/Soluti, VIDaaS/Valid, NeoID/Serpro, SafeID/Safeweb) | Fase 7 (integração real; mock não bloqueia) | [DECISÃO PENDENTE — Eduardo] |
| Provedor de PIX (candidatos: Mercado Pago, Efí) | Fase 2 (integração real; mock não bloqueia) | [DECISÃO PENDENTE — Eduardo] |
| WhatsApp: Meta Cloud API vs. Twilio | Fase 8 (mock não bloqueia) | [DECISÃO PENDENTE — Eduardo] |
| Política de retenção de mídia bruta pós-entrega | Fase 9 | [DEFINIR prazo em meses] |

Stack de frontend é **proposta aceita salvo objeção antes da Fase 1**: Django templates + Tailwind CSS + HTMX + Alpine.js (ver justificativa em Arquitetura). Se o Eduardo preferir SPA, parar e discutir antes da Fase 1.

## Stack

- Python 3.12+, Django 5.2 LTS, PostgreSQL 16+
- Celery + Redis (filas: `media`, `docs`, `ia`, `notify`)
- Storage S3-compatível via django-storages/boto3 (MinIO no dev/compose)
- ffmpeg (extração de frames de vídeo)
- API Anthropic (Messages; Batch API onde a latência permitir) — modelos e limites vigentes: consultar https://docs.claude.com antes de fixar strings de modelo; modelo configurável por env var
- Geração de PDF: WeasyPrint (HTML/CSS → PDF, reaproveita tokens da identidade) [proposta]
- Assinatura: pyHanko para PAdES; assinatura remota via adapter de provedor cloud — **confirmar na doc do pyHanko o fluxo de assinatura externa/interrompida antes de implementar**
- Upload resumível no browser: Uppy com multipart S3 presigned [proposta — verificar plugin atual na doc do Uppy]
- Frontend: Django templates + Tailwind + HTMX + Alpine (sem build de SPA)
- Deploy: Docker Compose em VPS, Caddy como proxy/TLS, GitHub Actions (lint + testes), Sentry, Flower

Justificativa do frontend: projeto solo, backend Django já decidido, páginas públicas precisam de SSR/SEO, e o único componente rico em JS é o uploader. Um stack só reduz custo de manutenção.

## Arquitetura

### Apps Django (monólito modular)

```
justavalia/
  core/         # settings, saúde, auditoria, usuários
  pedidos/      # modelo Pedido + máquina de estados + timeline
  pagamentos/   # adapter PIX (MockPix em dev)
  uploads/      # presigned URLs, manifesto de mídia, protocolo guiado
  pipeline/     # tasks Celery: frames, extração de documentos, análise
  triagem/      # score de risco → fast_lane / deep_lane
  ptam/         # template do parecer, geração de rascunho, render PDF
  assinatura/   # adapter ICP (MockSigner em dev), trilha de auditoria
  notificacoes/ # adapter WhatsApp/e-mail (ConsoleNotifier em dev)
  site_publico/ # páginas públicas (identidade visual)
  dashboard/    # revisão interna do avaliador
```

### Máquina de estados do Pedido

Implementação própria (enum + tabela de transições permitidas + guards + log imutável de transição com ator/timestamp). Não usar lib de FSM sem verificar manutenção ativa.

```
DRAFT → AWAITING_PAYMENT → AWAITING_UPLOAD → PROCESSING
PROCESSING → PENDENCY (item faltante; notifica e volta a AWAITING_UPLOAD)
PROCESSING → IN_TRIAGE → DRAFTING → IN_REVIEW
IN_REVIEW → PENDENCY | APPROVED_FOR_SIGNATURE
APPROVED_FOR_SIGNATURE → SIGNED → DELIVERED
Qualquer estado pré-SIGNED → CANCELLED
```

Regras invioláveis da máquina:
1. `APPROVED_FOR_SIGNATURE → SIGNED` só ocorre por ação autenticada do avaliador no dashboard (reautenticação/confirmação explícita no ato). Nunca por task, cron, webhook ou IA.
2. Toda transição registra ator, timestamp e payload no log de auditoria.
3. Estados e transições têm testes exaustivos (transições proibidas devem falhar).

### Pipeline (Celery)

1. **Mídia:** vídeo → ffmpeg extrai frames (~1 fps + keyframes), descarta borrados/duplicados; fotos normalizadas; tudo com hash e timestamp de recebimento.
2. **Documentos:** matrícula, IPTU etc. → extração estruturada via visão da API Anthropic (área, nº de matrícula, endereço, proprietário) → checagem de completude contra o checklist do protocolo.
3. **Análise do imóvel:** frames + fotos → descrição de cômodos, estado de conservação, flags de inconsistência (ex.: mídia que não bate com endereço/documentos) → alimenta triagem.
4. **Rascunho PTAM:** prompt com dados extraídos + comparáveis (módulo `avm/` interno, escopo regional — não sobre-engenheirar cobertura nacional) → rascunho estruturado por seção. Usar Batch API quando o lote tolerar latência.
5. Falhas de task: retry com backoff; erro persistente → estado PENDENCY com motivo legível para o cliente.

### Triagem

Score de risco com insumos: tipo de imóvel, confiança do AVM, dispersão dos comparáveis, flags de vídeo, completude documental. Saída: `fast_lane` (revisão curta) ou `deep_lane` (revisão aprofundada). Pesos em tabela configurável, com log do score e dos insumos em cada pedido (explicabilidade).

## Guardrails de produto — INEGOCIÁVEIS (aplicam-se a qualquer código ou texto gerado)

1. Nunca implementar auto-assinatura, assinatura em lote sem revisão, ou bypass do estado IN_REVIEW.
2. O template do PTAM contém obrigatoriamente a seção "Pressupostos, Ressalvas e Fatores Limitantes", incluindo a declaração de que a vistoria foi remota, por qual meio e em que data. O campo "data da vistoria" nunca sugere visita presencial que não houve.
3. Nenhum texto do sistema (site, PTAM, notificações, prompts de IA) afirma validade para financiamento bancário, perícia judicial ou fins que exijam laudo de engenharia com ART. Os prompts enviados à API devem conter essa restrição explicitamente.
4. LGPD: coletar o mínimo; consentimento registrado (timestamp + IP + versão do termo); mídia e documentos criptografados at rest; acesso logado; rotina de expurgo conforme política de retenção [DEFINIR]; endpoint de exclusão de dados.
5. Segredos apenas em `.env`/secret manager, nunca no repositório. `.env.example` sempre atualizado.

## Orquestração multiagente

**Sessão principal (orquestrador): Claude Fable 5** — selecionar via `/model` no início da sessão (se indisponível no plano, usar o Opus mais recente e registrar em docs/PROGRESSO.md).

O orquestrador: planeja cada fase, decompõe em tarefas, delega, integra, roda a suíte de testes e decide. **Não delega**: decisões de arquitetura, máquina de estados, triagem, assinatura, pagamentos e qualquer guardrail acima.

Subagentes de projeto — criar em `.claude/agents/` na Fase 0 exatamente com os arquivos abaixo:

`.claude/agents/revisor.md`
```markdown
---
name: revisor
description: Revisa código ao final de cada fase e obrigatoriamente qualquer mudança que toque assinatura, pagamentos, máquina de estados, uploads ou dados pessoais (LGPD). Use proactively antes de cada commit de fase. Verifica segurança, corretude, testes e conformidade com os guardrails do CLAUDE.md.
tools: Read, Grep, Glob, Bash
model: opus
---
Você é revisor sênior de segurança e corretude. Leia CLAUDE.md primeiro; os guardrails de produto são critérios de reprovação. Rode a suíte de testes. Produza: lista priorizada de problemas (arquivo:linha, correção sugerida), riscos de segurança/LGPD, e veredito APROVADO/REPROVADO com motivo. Não edite código.
```

`.claude/agents/dev-backend.md`
```markdown
---
name: dev-backend
description: Implementa tarefas de backend bem especificadas e de risco baixo/médio - models, views, forms, tasks Celery de rotina, serializers, migrações, testes, fixtures, configuração. Use para toda implementação backend que NÃO envolva assinatura, pagamentos ou a máquina de estados.
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---
Você implementa exatamente a tarefa especificada pelo orquestrador, seguindo as convenções do CLAUDE.md. Escreva testes junto com o código. Não tome decisões de arquitetura: se a especificação estiver ambígua, pare e devolva a dúvida.
```

`.claude/agents/dev-frontend.md`
```markdown
---
name: dev-frontend
description: Implementa templates Django, componentes Tailwind/HTMX/Alpine e páginas do site público a partir dos tokens e assets da identidade visual em design/. Use para todo trabalho de template, CSS e interação de frontend.
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---
Você constrói o frontend usando exclusivamente os tokens de design/tokens.md (cores, tipografia, espaçamento) derivados da identidade visual. Nada de valores hex soltos no código: sempre variáveis/classes do tema. Acessibilidade básica obrigatória: contraste, foco visível, reduced motion. Textos de interface em pt-BR.
```

`.claude/agents/pesquisador.md`
```markdown
---
name: pesquisador
description: Pesquisa documentação externa e devolve resumos com fontes - APIs de provedores (PIX, WhatsApp, ICP-Brasil), pyHanko, Uppy, Anthropic API. Use antes de implementar qualquer integração externa, para confirmar sintaxe e capacidades atuais.
tools: Read, WebFetch, WebSearch
model: sonnet
---
Você pesquisa e resume documentação técnica atual. Sempre cite URL e data. Diferencie claramente o que está confirmado na doc oficial do que é inferência. Nunca invente nomes de métodos ou endpoints; se a doc não confirmar, diga.
```

Política de delegação:
- **opus (revisor):** review obrigatório ao fim de cada fase e em todo diff que toque os módulos críticos. Veredito REPROVADO bloqueia o commit da fase.
- **sonnet (dev-backend/dev-frontend):** implementação de rotina com especificação fechada. **pesquisador:** antes de cada integração externa.
- Tarefas paralelizáveis e independentes podem rodar em subagentes simultâneos; integração sempre pelo orquestrador.

## Fases (executar em ordem; parar para aprovação do Eduardo ao fim de cada uma)

**Fase 0 — Fundação.** Repo, pyproject, Django skeleton com apps acima, Docker Compose (web, worker, beat, redis, postgres, minio), Makefile, CI (lint ruff + pytest), pre-commit, `.env.example`, criação dos 4 subagentes, docs/PROGRESSO.md. Aceite: `make up` sobe tudo; `make test` verde.

**Fase 1 — Identidade → tema.** Localizar o `.zip` da identidade visual na raiz do projeto, descompactar em `design/`, inventariar (logos, fontes, cores, HTML de referência das páginas), extrair `design/tokens.md` (hex, tipografia, espaçamentos) e configurar o tema Tailwind a partir dele. Aceite: página de styleguide interna renderizando todos os tokens e componentes base.

**Fase 2 — Site público.** Páginas: Home, Como funciona, Para advogados, Quem assina, FAQ, Política de privacidade e Termos (esqueleto com [PLACEHOLDER] jurídico), a partir do HTML de referência do design. Copy: usar a do design; onde faltar, primeira pessoa do singular, tom direto, respeitando o guardrail 3. Aceite: Lighthouse mobile ≥ 90 em performance/acessibilidade nas páginas públicas.

**Fase 3 — Pedido + pagamento (mock).** Modelo Pedido, máquina de estados completa com testes, fluxo público de criação de pedido, adapter `pagamentos/` com MockPix (aprovação simulada) e interface documentada para o provedor real. Aceite: pedido navega DRAFT → AWAITING_UPLOAD via mock, com timeline auditada.

**Fase 4 — Upload resumível + protocolo guiado.** Presigned multipart no S3/MinIO, UI de upload (Uppy) com o roteiro guiado (fachada, ambientes, documentos), manifesto de mídia com hash, validação de completude. Aceite: upload de vídeo de 500 MB sobrevive a queda de conexão e retoma.

**Fase 5 — Pipeline de processamento.** Tasks Celery: frames (ffmpeg), extração de documentos (visão Anthropic), análise de mídia, flags. Estado PROCESSING → IN_TRIAGE ou PENDENCY. Aceite: caso de teste completo processado ponta a ponta com fixtures reais fornecidas pelo Eduardo.

**Fase 6 — Triagem + rascunho PTAM + PDF.** Score de triagem configurável e logado; geração do rascunho por seção via API (Batch quando aplicável); render do PDF com WeasyPrint usando o template com bloco de vistoria remota e ressalvas obrigatórias. Aceite: PDF de rascunho fiel ao template, com todas as seções do Art. 5º da Res. COFECI 1.066/2007 presentes.

**Fase 7 — Dashboard de revisão + assinatura.** Fila fast/deep lane, editor de revisão do rascunho, diff do que a IA gerou vs. editado, ação de aprovação com reautenticação, adapter `assinatura/` com MockSigner (certificado de teste autoassinado via pyHanko) e interface para provedor cloud real. Aceite: fluxo aprovar → assinar (mock) → SIGNED com trilha de auditoria completa; impossível assinar fora do dashboard (testado).

**Fase 8 — Entrega + notificações.** Link seguro de download (presigned com expiração), página de status do pedido para o cliente, adapter `notificacoes/` (ConsoleNotifier em dev; interface para WhatsApp Cloud API/Twilio), e-mails transacionais. Aceite: cliente fictício recebe notificação (console) e baixa o PDF.

**Fase 9 — LGPD + hardening + deploy.** Rotina de expurgo, endpoint de exclusão, rate limiting, headers de segurança, backup do Postgres, Sentry, Flower, compose de produção com Caddy, runbook de deploy no VPS. Aceite: checklist de segurança do revisor APROVADO; deploy documentado executável.

Ao concluir cada fase: atualizar docs/PROGRESSO.md, mover detalhes da fase concluída deste arquivo para docs/ROADMAP.md (manter este CLAUDE.md enxuto).

## Convenções de engenharia

- Identificadores de código em inglês; exceção para termos jurídicos sem boa tradução (`ptam`, `ressalvas`, `matricula`, `vistoria`), sem acentos. Strings de UI em pt-BR.
- Testes com pytest + pytest-django; máquina de estados, triagem e assinatura exigem cobertura de casos negativos.
- Migrações sempre revisadas antes de commit; nunca `--fake` sem justificativa registrada.
- Commits pequenos por tarefa, mensagem em pt-BR no imperativo, referenciando a fase (ex.: `F4: adiciona manifesto de midia com hash`).
- Toda integração externa atrás de interface + implementação mock; troca por env var.
- Nunca escrever chaves reais em código, fixtures ou logs.

## Comandos (Makefile — criar na Fase 0)

`make up` (compose dev) · `make test` · `make lint` · `make worker` · `make shell` · `make seed` (dados de exemplo) · `make styleguide`

## Checklist de Go-Live (fora do escopo do código — depende do Eduardo)

- [ ] Credenciais do provedor ICP-Brasil escolhido + certificado cloud ativo
- [ ] Conta e credenciais do provedor PIX
- [ ] WhatsApp Business/Twilio: número, verificação Meta, templates de mensagem aprovados
- [ ] Domínio + DNS + e-mail transacional (SPF/DKIM)
- [ ] Textos jurídicos finais: Termos, Privacidade, Declaração de Veracidade, Termo de consentimento da vídeo-vistoria (revisão por advogado)
- [ ] Foto, bio, nº CRECI e nº CNAI para o site
- [ ] Política de retenção de mídia definida
- [ ] VPS provisionado e chaves de deploy

## Referências

- Subagentes do Claude Code: https://code.claude.com/docs/en/sub-agents
- API Anthropic (modelos, Batch): https://docs.claude.com
- Norma de referência do PTAM: Resolução COFECI 1.066/2007, Art. 5º (documento interno: resumo_decisoes_ptam_remoto.md)
