# Handoff: Site institucional Justavalia

## Overview
A Justavalia é um serviço brasileiro de avaliação de imóveis 100% remoto. O cliente envia documentos, fotos e vídeo do imóvel por um roteiro guiado; a análise de mercado é acelerada por tecnologia; e um avaliador credenciado (CRECI e CNAI) revisa e **assina pessoalmente** cada parecer com assinatura digital ICP-Brasil. O produto final é um **PTAM — Parecer Técnico de Avaliação Mercadológica** — em PDF, entregue em até 5 dias úteis, por R$ 299 (residencial urbano).

Este pacote cobre a **identidade visual** + **5 páginas** do site institucional:
1. **Home** — hero, barra de confiança, casos de uso, como funciona, anatomia do PTAM, transparência de escopo, preço, FAQ curto, CTA final.
2. **Como funciona** — linha do tempo, checklist de documentos, roteiro de fotos/vídeo, privacidade.
3. **Para advogados e escritórios** — canal de aquisição principal (indicadores).
4. **Quem assina** — página de credibilidade do avaliador.
5. **FAQ** — perguntas completas.

**Posicionamento central para preservar:** *não é uma ferramenta self-service — é um serviço com responsabilidade profissional.* A assinatura é o produto. A referência mental é um "cartório digital bem projetado".

## About the Design Files
Os arquivos em `design_reference/` são **referências de design criadas em HTML** — protótipos que mostram a aparência e o comportamento pretendidos, **não** código de produção para copiar diretamente. Eles usam um runtime interno de componentes (`.dc.html` + `support.js`) só para prototipagem.

A tarefa é **recriar esses designs no ambiente do codebase de destino** (React/Next, Vue, Astro, etc.), usando os padrões e bibliotecas já estabelecidos ali. Se ainda não houver ambiente, escolha o framework mais adequado — para um site institucional majoritariamente estático e mobile-first, **Astro ou Next.js (App Router) com Tailwind** são boas escolhas. Use `tokens.css` como fonte de verdade dos valores; ele pode ser importado direto ou traduzido para o `theme` do Tailwind.

## Fidelity
**Alta fidelidade (hifi).** Cores, tipografia, espaçamento e estados são finais. Recrie a UI fielmente. Onde há `clamp()` nos títulos, mantenha o comportamento responsivo. Todos os hex e medidas estão documentados abaixo e em `tokens.css`.

---

## Design Tokens
Fonte de verdade: **`tokens.css`** (variáveis CSS + utilitários). Resumo:

### Cores
| Token | Hex | Uso |
|---|---|---|
| `--jv-tinta` | `#16302B` | Base escura: títulos, footer, seções escuras, hero "tinta" |
| `--jv-tinta-900` | `#0E211D` | Fundos mais profundos |
| `--jv-tinta-700` | `#22423A` | Selo marca-d'água sobre fundo escuro |
| `--jv-tinta-border` | `#2A473F` | Divisores sobre escuro |
| `--jv-papel` | `#F6F3EC` | Fundo padrão da página |
| `--jv-papel-card` | `#FDFCF8` | Cards, superfície do documento |
| `--jv-papel-border` | `#E4DECF` | Borda de cards |
| `--jv-linha` | `#DDD6C8` | Borda do header, divisores sobre papel |
| `--jv-cobre` | `#B4611F` | **Acento único**: CTA, selo, eyebrows, números de passo |
| `--jv-cobre-hover` | `#94500F` | Hover do CTA |
| `--jv-cobre-claro` | `#C98A4B` | Acento sobre fundo escuro |
| `--jv-texto` | `#3C4742` | Texto corrido sobre papel |
| `--jv-texto-suave` | `#5B655F` | Legendas/secundário |
| `--jv-texto-escuro-suave` | `#C4CDC6` | Texto sobre fundo tinta |
| `--jv-texto-escuro-legenda` | `#8FA098` | Legendas sobre fundo tinta |

> **Não introduzir** azul-corporativo, roxo/gradiente de IA, glassmorphism, dourado kitsch. O acento é **um só**: o cobre.

### Tipografia (Google Fonts)
- **Títulos** — `Newsreader` (serifada editorial), peso 500–600. Autoridade documental.
- **Corpo e interface** — `Source Sans 3` (sans humanista), 400–700.
- **Dados/registros/carimbos** — `Spline Sans Mono`, 400–600, `letter-spacing` 1.6–2.4px, frequentemente em MAIÚSCULAS.

Import:
```
https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400..700&family=Source+Sans+3:wght@400..700&family=Spline+Sans+Mono:wght@400..600&display=swap
```
Escala de título: `clamp(32px, 4.4vw, 48px)` (h1) e `clamp(28px, 3.4vw, 40px)` (h2). Corpo 16–18.5px, line-height 1.55–1.65.

### Espaçamento & layout
- Contêiner largo: **1140px**; páginas de leitura (FAQ, Como funciona): **820px**; ambos `margin: 0 auto; padding: 0 20px`.
- Padding vertical entre seções: **72px** (topo) — ver `--jv-sp-*`.
- **Raio:** `4px` em botões/superfícies (discreto, documental); `999px` só no FAB do WhatsApp.
- **Sombras:** documento `0 18px 44px rgba(22,48,43,.16)`; card `0 14px 36px rgba(22,48,43,.12)`; FAB `0 6px 18px rgba(22,48,43,.28)`.
- **Ícones:** linha 1.5px, cantos retos, `currentColor` — ver `assets/icones.svg`.

---

## Marca / Assets
Ver pasta `assets/`.

- **Símbolo escolhido (opção 2c): monograma-carimbo "J".** Bloco de carimbo de linha dupla com um "J" em Newsreader e uma sublinha em cobre (a rubrica). Funciona monocromático, como favicon, avatar de WhatsApp e marca-d'água no PDF.
  - `logo-simbolo-monograma.svg` — versão escura (sobre papel)
  - `logo-simbolo-monograma-claro.svg` — versão clara (traços em cobre-claro `#C98A4B`, sobre fundo tinta)
  - `logo-lockup-horizontal.svg` — símbolo + wordmark "Justavalia"
- **Rubrica** (`rubrica.svg`) — o elemento-assinatura da marca. Aparece dentro do símbolo (a sublinha), na assinatura do documento PTAM e pode servir de divisor de seções.
- **Ícones** (`icones.svg`) — documento, vídeo, assinatura, prazo/calendário, verificação, check. `<symbol>` com `currentColor`.
- `homepage-preview.png` — captura completa da Home renderizada (909px de largura), para referência visual.

> O símbolo é desenhado com SVG + `<text>` em Newsreader. Para produção, considere converter o "J" em `<path>` (outline) para não depender da fonte carregar, **ou** garanta que a Newsreader esteja disponível antes de renderizar o SVG (ex.: inline no HTML após o CSS de fontes).

---

## Componentes reutilizáveis
Referência: `design_reference/*.dc.html`.

### Header (`Header.dc.html`)
- `position: sticky; top: 0; z-index: 60`, fundo `--jv-papel`, borda inferior `1px solid --jv-linha`.
- Contêiner 1140px, `display:flex; align-items:center; gap:14px 22px; padding:12px 20px`.
- Esquerda: lockup (símbolo 38px + wordmark Newsreader 23px/600). Direita (`margin-left:auto`): nav em `Source Sans 3` 15.5px `#3C4742` + **CTA cobre** "Pedir minha avaliação".
- Estado ativo do link: `border-bottom: 2px solid --jv-cobre` (prop `ativa`).
- **Responsivo/mobile:** a nav deve colapsar em menu hambúrguer < ~720px (o protótipo usa `flex-wrap`; implemente um drawer no codebase). Manter o CTA sempre visível.

### Footer (`Footer.dc.html`)
- Fundo `--jv-tinta`, texto `#D9DED9`. Grid `repeat(auto-fit, minmax(220px,1fr))`, `gap:36px`, padding `56px 20px 32px`.
- Colunas: marca + descrição + `CRECI [nº] · CNAI [nº]`; Páginas; Contato e legal (WhatsApp, e-mail, Política de privacidade LGPD, Termos).
- Barra inferior: `CNPJ [preencher]` + "PARECERES VERIFICÁVEIS NO VALIDADOR OFICIAL DO ITI", em mono 11.5px.

### Botão de WhatsApp flutuante (`Zap.dc.html`)
- `position: fixed; bottom:20px; right:20px; z-index:80`. Pill cobre, sombra FAB, ícone + "Falar no WhatsApp".
- **Persistente em todas as páginas.** `href` para `https://wa.me/55<NÚMERO>`.

### Selo (`Selo.dc.html`)
- 3 variantes: `monograma` (escolhida), `circular`, `carimbo`. Props: `cor`, `cor2` (traço da rubrica), `tamanho`. Recrie como um componente SVG que aceita cor/tamanho.

### Card de etapa
- Duas formas em uso: **card** (`--jv-papel-card` + borda) e **borda-topo** (`border-top: 2px solid --jv-tinta` com número de passo `01–04` em mono cobre). Ver seção "Como funciona".

### Bloco "Serve / (limites)"
- **Importante (mudança recente):** na Home **não há mais** um card vermelho separado "Não serve para". Existe um único card **"SERVE PARA"** (cabeçalho `--jv-tinta`, itens com ícone check), e os limites aparecem como **nota discreta ao pé do card**: *"Não cobre financiamento bancário, perícia judicial nem laudo de engenharia com ART. Entenda por quê →"* (link ao FAQ). Preserve exatamente esse tratamento.
- A transparência de escopo detalhada permanece no **FAQ** e na página **Advogados** — não removê-la de lá.

---

## Screens / Views

### 1. Home (`Home.dc.html`)
Ordem das seções (todas em contêiner 1140px salvo indicado):

1. **Hero** — eyebrow mono "PTAM · PARECER TÉCNICO…"; h1 *"Seu imóvel avaliado por um profissional credenciado. 100% online, em 5 dias úteis."*; subhead explicando o PTAM e quem assina; CTA cobre "Pedir minha avaliação" + botão ghost "Como funciona"; linha mono "R$ 299 · PREÇO FIXO · IMÓVEL RESIDENCIAL URBANO". Visual à direita: **mockup do documento assinado** (não foto de imóvel) com o **símbolo** sobreposto rotacionado −9°. Grid `auto-fit minmax(300px,1fr)`, gap 48px.
   - Duas variações de tema no protótipo (prop `heroVariante`): **papel** (fundo `--jv-papel`) e **tinta** (fundo `--jv-tinta`, texto claro, marca-d'água do símbolo grande). Implemente **papel** como padrão; tinta é opcional.
2. **Barra de confiança** — faixa `--jv-tinta`, uma linha em mono 12px: `CRECI [nº] · CNAI [nº] · ASSINATURA DIGITAL ICP-BRASIL · VERIFICÁVEL NO VALIDADOR OFICIAL DO ITI`.
3. **Para que serve** — eyebrow + h2; grid `auto-fit minmax(210px,1fr)` de 5 cards (ícone + h3 Newsreader 20px + parágrafo): Inventário e partilha; Divórcio; ITCMD e planejamento patrimonial; Compra, venda e negociação; Atualização de patrimônio.
4. **Como funciona (resumo)** — 4 colunas `border-top:2px solid --jv-tinta`, número `01–04` mono cobre, h3, parágrafo. Link "Ver o processo completo…". Passos: (1) você envia docs/fotos/vídeo por roteiro guiado; (2) analisamos o mercado com tecnologia; (3) avaliador credenciado revisa e assina; (4) você recebe o PDF em até 5 dias úteis.
5. **O que você recebe (anatomia do PTAM)** — layout 2 colunas: título à esquerda; lista à direita de 5 itens marcados `§1–§5` (mono cobre): Identificação do imóvel; Metodologia e comparativos; Registro fotográfico; Pressupostos e ressalvas; Assinatura digital verificável.
6. **Transparência de escopo** — card único "SERVE PARA" + nota de limites (ver "Bloco Serve / limites" acima).
7. **Preço** — seção `--jv-tinta`: "R$ 299" em Newsreader clamp(56–84px), "imóvel residencial urbano"; nota "Comercial, rural e alto valor: sob consulta"; CTA cobre.
8. **FAQ curto** — contêiner 820px, 3–4 `<details>` (accordion nativo), link "Ver todas as perguntas →".
9. **CTA final** — símbolo centralizado, h2, CTA cobre.
10. **Footer** + **FAB WhatsApp**.

### 2. Como funciona (`Como-funciona.dc.html`) — contêiner 820px
- Intro (eyebrow, h1 *"Do pedido à entrega, em até 5 dias úteis."*, parágrafo).
- **Linha do tempo vertical** — `border-left: 2px solid --jv-tinta` com bolinhas cobre (`--jv-cobre`, borda 3px `--jv-papel`); a última bolinha é `--jv-tinta`. Etapas: DIA 0 (pedido, roteiro), DIAS 1–2 (envio), DIAS 2–4 (análise), DIAS 4–5 (revisão/assinatura), ATÉ O 5º DIA ÚTIL (entrega). Cada etapa: label mono cobre + h2 Newsreader 23px + parágrafo.
- **Checklist de documentos** — 2 cards: "OBRIGATÓRIOS" (matrícula atualizada, IPTU) com ícone check; "AJUDAM, SE VOCÊ TIVER" (habite-se, planta) com ícone "+".
- **Roteiro de fotos/vídeo** — 3 colunas border-topo: 01 Fachada, 02 Ambientes, 03 Detalhes.
- **Se faltar algo** (card papel) + **Privacidade LGPD** (card tinta). CTA cobre.

### 3. Para advogados e escritórios (`Advogados.dc.html`) — contêiner 1140px
- **Hero tinta** com marca-d'água do símbolo; eyebrow "PARA ADVOGADOS, CARTÓRIOS E CONTADORES"; h1 *"A avaliação não precisa ser o gargalo do inventário."*; parágrafo (dor: laudos de engenharia caros/demorados em casos que não os exigem); CTA "Fale com a gente".
- **Por que indicar** — 4 cards: Prazo previsível; Responsabilidade profissional; Verificável; Custo proporcional.
- **Reconhecimento e limites** — 2 cards lado a lado:
  - "O QUE PODEMOS AFIRMAR": PTAM reconhecido pela Receita Federal como documento hábil para fundamentar valor (**IN RFB 2.091/2022**).
  - "O QUE NÃO PROMETEMOS": **não** prometer aceitação universal pelas SEFAZ estaduais para ITCMD — regras variam por estado. **Preservar essa ressalva literalmente.**
- **Parceria** — 3 passos de indicação (`[modelo de indicação — placeholder para condições]`). CTA "Fale com a gente" + material de apoio.

### 4. Quem assina (`Quem-assina.dc.html`) — contêiner 1140px→820px
- Topo 2 colunas: à esquerda h1 *"Todo parecer tem nome, registro e responsabilidade."* + parágrafo; à direita **card de perfil** (foto placeholder circular hachurada, `[Nome do Avaliador]`, `CRECI [nº] · CNAI [nº]`, bio placeholder, rubrica + "ASSINATURA DIGITAL · ICP-BRASIL").
- **O modelo, sem rodeio** — 3 blocos: "O que a tecnologia faz" / "O que o avaliador faz" / "Por que isso importa" (bloco tinta). Mensagem: a tecnologia acelera; a responsabilidade é de quem assina.
- **Credenciais** — 3 colunas border-topo: CRECI, CNAI, ICP-Brasil. CTA cobre.

### 5. FAQ (`FAQ.dc.html`) — contêiner 820px
- Eyebrow, h1 *"Respostas diretas, sem juridiquês."*, intro.
- 7 `<details>` (accordion): O que é um PTAM e quem pode emitir? · A vistoria por vídeo vale? · Serve para financiamento bancário? · Quanto tempo demora? · Como pago? · E se meu imóvel for comercial ou rural? · Meus documentos e vídeos ficam protegidos? (LGPD).
- CTA final "Falar no WhatsApp".

> **A cópia completa em pt-BR de cada seção está nos arquivos `.dc.html`** — use-os como fonte literal de texto. Todo o conteúdo já respeita o tom de voz do briefing.

---

## Interactions & Behavior
- **CTA único por página**, sempre levando ao WhatsApp (`wa.me/55<NÚMERO>`). Botões nomeiam a ação ("Pedir minha avaliação", "Falar no WhatsApp", "Fale com a gente") — nunca "Enviar".
- **FAB do WhatsApp** fixo e persistente em todas as páginas.
- **Accordions** (FAQ) usam `<details>/<summary>` nativos — mantenha o comportamento; some/expande no clique.
- **Header sticky**; link da página atual sublinhado em cobre.
- **Hover:** CTA cobre → `--jv-cobre-hover`; links de nav → `--jv-tinta`; links do footer → sublinhado.
- **Transições** curtas (~0.15s) em background de botões. Sem animações de entrada elaboradas.

## Responsive behavior
- **Mobile-first** (maior parte do tráfego é mobile). Grids usam `auto-fit / minmax(...)` e colapsam sozinhos; heros viram 1 coluna.
- Header: implementar **drawer/hambúrguer** < ~720px (o protótipo apenas quebra a linha).
- Título com `clamp()` já escala; garanta padding lateral de 20px em telas pequenas.
- Mockups de documento: `width: min(350px, 86vw)`.

## Accessibility
- Contraste: cobre `#B4611F` sobre papel `#F6F3EC` e branco em cobre atendem AA para os tamanhos usados; texto corpo é `#3C4742` sobre papel.
- **Foco de teclado visível:** `outline: 2px solid` — cobre sobre papel, papel sobre fundo escuro (tokens `--jv-focus` / `--jv-focus-escuro`). Não remover outlines.
- **`prefers-reduced-motion: reduce`** já contemplado em `tokens.css` (zera animações/transições).
- SVGs decorativos com `aria-hidden`; ícones informativos com `role="img"` + `aria-label`.
- Estrutura semântica: um `<h1>` por página, `<nav aria-label>`, landmarks `<header>/<main>/<footer>`.

## State Management
Site majoritariamente estático. Estado local mínimo:
- Abertura/fechamento do **menu mobile** (header).
- Abertura dos **accordions** (nativo, sem estado JS se usar `<details>`).
- Prop de tema do hero (`papel`/`tinta`) — decisão de build, não runtime.
Sem data fetching. O único "backend" é o link do WhatsApp.

## Placeholders a preencher (em colchetes no design)
- `[NOME DO AVALIADOR]`, bio e foto (Quem assina)
- `CRECI [nº]`, `CNAI [nº]`
- Número de **WhatsApp** (`wa.me/55...`), **e-mail**, **CNPJ**
- `[modelo de indicação]` (Advogados)
- Política de privacidade (LGPD) e Termos de uso (links do footer)

## Copy — regras inegociáveis
- Chamar o produto de **"parecer técnico" / "PTAM"** — **evitar a palavra "laudo"**.
- Evitar "avaliação grátis", "em minutos", superlativos vazios.
- Honestidade como estratégia: os limites (não serve para financiamento/perícia/ART) aparecem com clareza, não em letra miúda.
- Mencionar **IN RFB 2.091/2022** é ok; **não** prometer aceitação universal por SEFAZ para ITCMD.

## Files (nesta pasta)
- `tokens.css` — tokens + utilitários (fonte de verdade dos valores).
- `assets/` — logos SVG (monograma escuro/claro, lockup), rubrica, ícones, `homepage-preview.png`.
- `design_reference/` — protótipos HTML das 5 páginas + componentes (Header, Footer, Selo, Zap) + `support.js` (runtime só de prototipagem — **não portar**). Use como referência de layout e **fonte literal da cópia pt-BR**.

### Como abrir os protótipos
Os `.dc.html` precisam do `support.js` ao lado (já incluído). Abra qualquer um num servidor estático local (ex.: `npx serve design_reference`) para ver o comportamento pretendido. Não é necessário rodá-los para implementar — a cópia e o layout estão documentados aqui e legíveis no HTML.
