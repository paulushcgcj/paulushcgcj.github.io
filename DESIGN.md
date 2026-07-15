---
name: Modern-Technical Editorial
colors:
  light:
    surface: '#faf9f7'
    surface-dim: '#dadad8'
    surface-bright: '#faf9f7'
    surface-container-lowest: '#ffffff'
    surface-container-low: '#f4f3f1'
    surface-container: '#efeeec'
    surface-container-high: '#e9e8e6'
    surface-container-highest: '#e3e2e0'
    on-surface: '#1a1c1b'
    on-surface-variant: '#434750'
    inverse-surface: '#2f3130'
    inverse-on-surface: '#f1f1ef'
    outline: '#737781'
    outline-variant: '#c3c6d2'
    surface-tint: '#325f9e'
    primary: '#1e4e8c'
    on-primary: '#ffffff'
    primary-container: '#9dc1ff'
    on-primary-container: '#00376f'
    inverse-primary: '#a8c8ff'
    secondary: '#b85c3e'
    on-secondary: '#ffffff'
    secondary-container: '#ff9472'
    on-secondary-container: '#772b11'
    tertiary: '#2f7a34'
    on-tertiary: '#ffffff'
    tertiary-container: '#84d280'
    on-tertiary-container: '#00410e'
    error: '#ba1a1a'
    on-error: '#ffffff'
    error-container: '#ffdad6'
    on-error-container: '#93000a'
    primary-fixed: '#d6e3ff'
    primary-fixed-dim: '#a8c8ff'
    on-primary-fixed: '#001b3d'
    on-primary-fixed-variant: '#134684'
    secondary-fixed: '#ffdbd0'
    secondary-fixed-dim: '#ffb59e'
    on-secondary-fixed: '#3a0b00'
    on-secondary-fixed-variant: '#7b2e14'
    tertiary-fixed: '#a6f6a0'
    tertiary-fixed-dim: '#8bd987'
    on-tertiary-fixed: '#002204'
    on-tertiary-fixed-variant: '#005314'
    background: '#faf9f7'
    on-background: '#1a1c1b'
    surface-variant: '#e3e2e0'
    border: '#e9e8e5'
  dark:
    surface: '#101319'
    surface-dim: '#101319'
    surface-bright: '#363940'
    surface-container-lowest: '#0b0e14'
    surface-container-low: '#191c22'
    surface-container: '#1d2026'
    surface-container-high: '#272a30'
    surface-container-highest: '#32353b'
    on-surface: '#e1e2eb'
    on-surface-variant: '#c3c6d2'
    inverse-surface: '#e1e2eb'
    inverse-on-surface: '#2d3037'
    outline: '#8d919b'
    outline-variant: '#434750'
    surface-tint: '#a8c8ff'
    primary: '#a8c8ff'
    on-primary: '#003062'
    primary-container: '#1e4e8c'
    on-primary-container: '#9dc1ff'
    inverse-primary: '#325f9e'
    secondary: '#ffb59e'
    on-secondary: '#5d1801'
    secondary-container: '#7b2e14'
    on-secondary-container: '#ff9b7b'
    tertiary: '#8bd987'
    on-tertiary: '#00390b'
    tertiary-container: '#065b19'
    on-tertiary-container: '#84d280'
    error: '#ffb4ab'
    on-error: '#690005'
    error-container: '#93000a'
    on-error-container: '#ffdad6'
    primary-fixed: '#d6e3ff'
    primary-fixed-dim: '#a8c8ff'
    on-primary-fixed: '#001b3d'
    on-primary-fixed-variant: '#134684'
    secondary-fixed: '#ffdbd0'
    secondary-fixed-dim: '#ffb59e'
    on-secondary-fixed: '#3a0b00'
    on-secondary-fixed-variant: '#7b2e14'
    tertiary-fixed: '#a6f6a0'
    tertiary-fixed-dim: '#8bd987'
    on-tertiary-fixed: '#002204'
    on-tertiary-fixed-variant: '#005314'
    background: '#101319'
    on-background: '#e1e2eb'
    surface-variant: '#32353b'
    border: '#434750'
typography:
  display-lg:
    fontFamily: Fraunces
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.01em
  display-lg-mobile:
    fontFamily: Fraunces
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Fraunces
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  article-body:
    fontFamily: Inter
    fontSize: 17px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: -0.01em
  code-inline:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.08em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-max: 1100px
  article-max: 720px
  gutter: 24px
  margin-mobile: 16px
  stack-unit: 8px
---

## Brand & Style

The brand personality is a fusion of academic rigor and modern engineering. It targets software architects and technical leads who value clarity, precision, and a sophisticated reading experience. The design style is **Modern-Editorial with Technical Accents** — a rigorous, grid-based editorial layout punctuated by a sophisticated palette of deep blues and warm terracotta, meant to feel authoritative and timeless while keeping the precision of a developer-centric tool.

The two modes are the same brand under different lighting, not two separate designs:

- **Dark mode** reads as an immersive, focused digital journal — a "Night Slate" environment for long, low-strain reading sessions.
- **Light mode** reads as a "Clean Lab" — a high-end technical manual or architectural blueprint, high-contrast and information-dense.

## Colors

Both palettes share the same token names and roles (Material 3–style: `primary` / `secondary` / `tertiary`, each with an `on-*` and `*-container` pair, plus a shared neutral/surface ramp). Only the tone assignment flips between modes:

- **Dark mode** assigns *light, high-chroma tints* to the base roles (`primary`, `secondary`, `tertiary`) so they read clearly against dark surfaces, while the deeper, more saturated version of each hue lives in `*-container` for larger fills.
- **Light mode** does the opposite: base roles carry the *deep, saturated* tone so they stay legible on a pale background, while `*-container` holds the lighter, softer tint for chips, tags, and large fills.

Role meaning is identical across modes:

- **Primary (Deep Blue family):** primary actions, navigation states, core branding, heading color. Conveys stability and technical reliability.
- **Secondary (Terracotta family):** highlights, callouts, links, and interactive/focus states. Warm, editorial contrast to the cool primary.
- **Tertiary (Forest Green family):** success states, code diffs, and technical readouts.
- **Neutral/Background:** dark mode uses a deep, warm charcoal slate (`#101319`) with progressively lighter surface containers to build depth; light mode uses a warm off-white (`#faf9f7`) with progressively darker/greyer surface containers, plus an explicit `border` token (`#e9e8e5` light / `#434750` dark) for the "blueprint" grid-line feel.
- **Text:** `on-surface` is high-contrast (near-white on dark, near-black on light) for body copy; `on-surface-variant` is a muted blue-grey used for metadata and secondary info in both modes.

## Typography

A single three-font type scale is shared, unchanged, across both modes — theming only touches color, never type:

- **Fraunces (Headlines — `display-lg`, `display-lg-mobile`, `headline-md`):** an expressive, chiseled serif used for impact. Provides an "editorial," stamped-onto-the-page feel that distinguishes the brand from generic tech blogs.
- **Inter (Body — `article-body`):** a highly legible, modern sans-serif at 17px/1.6 line-height, comfortable for long-form technical articles on any surface color.
- **JetBrains Mono (Technical/UI — `code-inline`, `label-caps`):** code snippets, tags, timestamps, and small labels. Anchors the design in the developer world and gives metadata a precise rhythm.

## Layout & Spacing

Both modes share one **Fixed-Fluid Hybrid** layout model on an 8px baseline grid.

- **Article Pages:** centered, narrow column (`article-max`: 720px) to maximize line-length readability for the Inter body face.
- **Dashboards/Lists:** 12-column grid with 24px gutters (`container-max`: 1100px).
- **Rhythm:** strict 8px (`stack-unit`) vertical rhythm; generous spacing lets the editorial typography feel premium rather than cramped. In light mode, explicit 1px `border` dividers between major sections reinforce the blueprint structure.
- **Mobile:** margins shrink to 16px (`margin-mobile`), multi-column grids collapse to a single stack.

## Elevation & Depth

Neither mode uses traditional drop shadows — depth comes from tone and outline instead:

- **Dark mode — Tonal Stacking:** each surface container steps a notch lighter than the one below it, creating a "lifted" appearance. Interactive elements use color shifts or 1px borders (primary blue / secondary terracotta) instead of shadows. A subtle 8px backdrop-blur is used on overlays and nav bars.
- **Light mode — Low-Contrast Outlines + Tonal Layering:** each surface container steps a notch darker/greyer than the background, and 1px solid `border` tokens define separation explicitly. Raised/active elements use a subtle offset border or a tint shift toward secondary terracotta rather than elevation.
- **Interactivity (both modes):** focus and active states are communicated with high-contrast color shifts (e.g. a button moving from Deep Blue to Terracotta), not z-axis movement.

## Shapes

The shape language is **Technical and Precise** in both modes — soft, not bubbly.

- **Standard elements:** 0.25rem (4px) corner radius (`rounded.DEFAULT`).
- **Large containers** (cards, modals, code blocks): 0.5rem (8px), via `rounded.lg`.
- **Interactive triggers** (buttons, inputs): stick to the standard 4px radius for a compact, technical look.

## Components

- **Buttons:** solid Deep Blue background with white/`on-primary` text for primary actions; ghost-style secondary buttons use a 1px secondary-terracotta border. Button labels use `label-caps` (monospaced) in both modes.
- **Code Blocks:** dark, professional palette regardless of page theme (code blocks stay dark-surfaced even on the light theme, for contrast and familiarity); headers show the language name in `label-caps`.
- **Chips/Tags/Badges:** `label-caps`, all-caps, monospaced text inside a subtle secondary- or tertiary-color tint (`*-container` tone).
- **Cards:** dark mode uses a `Surface 2` fill with a primary-blue 1px border on hover; light mode uses a 1px `border` outline by default, with a slightly darker header strip to separate metadata from content.
- **Inputs:** darker-than-surface fill in dark mode with a primary-color bottom border that expands on focus; base-surface fill with a 1px `border` in light mode, transitioning to secondary terracotta on focus.
- **Lists:** horizontal separators between items; hover uses a subtle background-tint shift rather than shadows or chevrons.
- **Technical Readouts:** a bordered box with a `label-caps` label in the top-left and `code-inline` data points inside — identical pattern in both modes.
- **Reading Progress Bar:** a thin, 2px terracotta line at the top of the viewport that fills as the user scrolls, shared by both modes.