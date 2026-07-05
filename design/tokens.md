# Tokens de design — Justavalia

Fonte de verdade dos **valores**: `design/tokens.css`. Fonte de verdade do **uso**:
`design/README.md`. Este arquivo consolida os tokens para o tema Tailwind e para os
subagentes de frontend. Regra de ouro visual: base documental sóbria (verde-**tinta** sobre
**papel** off-white) com **um único acento quente: cobre**. Não introduzir azul-corporativo,
roxo/gradiente de "IA", glassmorphism nem dourado.

## Cores

| Token Tailwind | Var CSS | Hex | Uso |
|---|---|---|---|
| `tinta` | `--jv-tinta` | `#16302B` | Base escura: títulos, footer, seções e hero escuros |
| `tinta-900` | `--jv-tinta-900` | `#0E211D` | Fundos mais profundos / hover de superfície escura |
| `tinta-700` | `--jv-tinta-700` | `#22423A` | Selo marca-d'água sobre escuro |
| `tinta-border` | `--jv-tinta-border` | `#2A473F` | Divisores sobre escuro |
| `papel` | `--jv-papel` | `#F6F3EC` | Fundo padrão da página |
| `papel-card` | `--jv-papel-card` | `#FDFCF8` | Cards, superfície do documento |
| `papel-border` | `--jv-papel-border` | `#E4DECF` | Borda de cards sobre papel |
| `linha` | `--jv-linha` | `#DDD6C8` | Borda de header / divisores sobre papel |
| `cobre` | `--jv-cobre` | `#B4611F` | **Acento único**: CTA, selo, eyebrow, nº de passo |
| `cobre-hover` | `--jv-cobre-hover` | `#94500F` | Hover do CTA |
| `cobre-claro` | `--jv-cobre-claro` | `#C98A4B` | Acento sobre fundo escuro |
| `texto` | `--jv-texto` | `#3C4742` | Texto corrido sobre papel |
| `texto-suave` | `--jv-texto-suave` | `#5B655F` | Legendas / secundário sobre papel |
| `texto-escuro-suave` | `--jv-texto-escuro-suave` | `#C4CDC6` | Texto sobre fundo tinta |
| `texto-escuro-legenda` | `--jv-texto-escuro-legenda` | `#8FA098` | Legendas sobre fundo tinta |

## Tipografia (Google Fonts)

| Token Tailwind | Var CSS | Família | Uso |
|---|---|---|---|
| `font-titulo` | `--jv-fonte-titulo` | `Newsreader`, Georgia, serif | Títulos — serifada editorial, peso 500–600 |
| `font-texto` | `--jv-fonte-texto` | `Source Sans 3`, system-ui, sans | Corpo e interface, 400–700 |
| `font-mono` | `--jv-fonte-mono` | `Spline Sans Mono`, ui-monospace | Dados/registros/carimbos, 400–600, tracking 1.6–2.4px, MAIÚSCULAS |

Import (Google Fonts):
`https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400..700&family=Source+Sans+3:wght@400..700&family=Spline+Sans+Mono:wght@400..600&display=swap`

Escala de título (responsiva): h1 `clamp(32px, 4.4vw, 48px)`; h2 `clamp(28px, 3.4vw, 40px)`;
h3 `20px`. Corpo `16–18.5px`, line-height `1.55–1.65`. Eyebrow: mono `12px`, tracking `2.4px`,
UPPERCASE, cor cobre.

## Espaçamento

| Token | Var CSS | Valor |
|---|---|---|
| `sp-1` | `--jv-sp-1` | `8px` |
| `sp-2` | `--jv-sp-2` | `12px` |
| `sp-3` | `--jv-sp-3` | `16px` |
| `sp-4` | `--jv-sp-4` | `20px` |
| `sp-5` | `--jv-sp-5` | `24px` |
| `sp-6` | `--jv-sp-6` | `32px` |
| `sp-7` | `--jv-sp-7` | `48px` |
| `sp-section` | `--jv-sp-section` | `72px` (padding vertical entre seções) |

## Layout, raio, sombras, foco

- Contêiner largo: `--jv-container` = **1140px**; leitura (FAQ/Como funciona):
  `--jv-container-texto` = **820px**; ambos `margin: 0 auto; padding: 0 20px`.
- Raio: `--jv-radius` = **4px** (botões/superfícies, discreto/documental);
  `--jv-radius-pill` = **999px** (só o FAB do WhatsApp).
- Sombras: doc `0 18px 44px rgba(22,48,43,.16)`; doc-escuro `0 22px 54px rgba(0,0,0,.35)`;
  card `0 14px 36px rgba(22,48,43,.12)`; FAB `0 6px 18px rgba(22,48,43,.28)`.
- Foco (a11y): `--jv-focus` = `2px solid cobre` (sobre papel);
  `--jv-focus-escuro` = `2px solid papel` (sobre tinta/cobre). **Nunca remover outlines.**
- `prefers-reduced-motion: reduce` zera animações/transições (já em tokens.css).

## Componentes base (do README/tokens.css)

- **Botão CTA primário** (`.jv-btn`): fundo cobre, texto papel, `padding 15px 26px`, raio 4px,
  `font-texto 17px/600`, hover → cobre-hover, foco visível. Sempre nomeia a ação (nunca "Enviar").
- **Botão secundário** (`.jv-btn-ghost`): contorno `1.5px tinta` sobre papel, hover `#ECE7DA`.
- **Card** (`.jv-card`): `papel-card` + borda `papel-border`, `padding sp-5`.
- **Eyebrow** (`.jv-eyebrow`): mono uppercase cobre, tracking 2.4px.
- **h1/h2/body** (`.jv-h1`/`.jv-h2`/`.jv-body`): ver escala acima.
- **Header** sticky (papel, borda `linha`), **Footer** tinta, **FAB WhatsApp** pill cobre fixo,
  **Selo/monograma** (SVG em `assets/`), **card de etapa** (borda-topo `2px tinta` + nº mono cobre).

## Assets de marca (`design/assets/`)

- `logo-simbolo-monograma.svg` (escuro/sobre papel), `logo-simbolo-monograma-claro.svg`
  (cobre-claro/sobre tinta), `logo-lockup-horizontal.svg` (símbolo + wordmark).
- `rubrica.svg` (elemento-assinatura), `icones.svg` (`<symbol>` currentColor: documento, vídeo,
  assinatura, prazo, verificação, check), `homepage-preview.png` (referência visual da Home).
