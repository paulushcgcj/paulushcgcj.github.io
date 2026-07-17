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
    secondary: '#0058be'
    on-secondary: '#ffffff'
    secondary-container: '#d8e2ff'
    on-secondary-container: '#001a42'
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
    secondary-fixed: '#d8e2ff'
    secondary-fixed-dim: '#adc6ff'
    on-secondary-fixed: '#001a42'
    on-secondary-fixed-variant: '#004395'
    tertiary-fixed: '#a6f6a0'
    tertiary-fixed-dim: '#8bd987'
    on-tertiary-fixed: '#002204'
    on-tertiary-fixed-variant: '#005314'
    background: '#f7f9fb'
    on-background: '#191c1e'
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
    secondary: '#adc6ff'
    on-secondary: '#001a42'
    secondary-container: '#004395'
    on-secondary-container: '#d8e2ff'
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
    secondary-fixed: '#d8e2ff'
    secondary-fixed-dim: '#adc6ff'
    on-secondary-fixed: '#001a42'
    on-secondary-fixed-variant: '#004395'
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

**Modern-Editorial with Technical Accents.** A grid-based editorial layout with deep blue and vibrant blue palette — authoritative, precise, developer-centric. Targets software architects and technical leads.

Two modes, one brand:

- **Dark mode** — "Night Slate." Immersive digital journal for long, low-strain reading.
- **Light mode** — "Clean Lab." High-contrast technical manual with information density.

## Colors

Material 3–style token system: `primary` / `secondary` / `tertiary` with `on-*` and `*-container` pairs, plus a shared neutral/surface ramp. Tone assignment flips between modes:

- **Dark mode:** base roles get *light, high-chroma* tints for legibility on dark surfaces; `*-container` holds the deeper, more saturated version.
- **Light mode:** base roles get *deep, saturated* tones for legibility on pale backgrounds; `*-container` holds the lighter, softer tint.

Role meaning stays constant:

- **Primary (Deep Blue):** primary actions, navigation, core branding, headings. Stability and reliability.
- **Secondary (Vibrant Blue):** highlights, callouts, links, focus states. Technical contrast to primary.
- **Tertiary (Forest Green):** success states, code diffs, technical readouts.
- **Neutral/Background:** dark uses deep charcoal slate (`#101319`) with lighter surface containers for depth; light uses cool off-white (`#f7f9fb`) with darker surface containers plus a `border` token (`#e9e8e5` light / `#434750` dark) for blueprint grid lines.
- **Text:** `on-surface` is high-contrast body copy (near-white on dark, near-black on light); `on-surface-variant` is muted blue-grey for metadata.

## Typography

Three-font scale, shared across both modes — theming touches color only, never type.

- **Fraunces (Headlines):** expressive, chiseled serif. Editorial feel that separates the brand from generic tech blogs.
- **Inter (Body):** legible sans-serif at 17px/1.6. Comfortable for long-form technical articles.
- **JetBrains Mono (Technical/UI):** code, tags, timestamps, small labels. Developer-world anchor with precise rhythm.

## Layout & Spacing

**Fixed-Fluid Hybrid** on an 8px baseline grid.

- **Article Pages:** centered column (`article-max`: 720px) for line-length readability.
- **Dashboards/Lists:** 12-column grid, 24px gutters (`container-max`: 1100px).
- **Rhythm:** strict 8px vertical rhythm. Light mode uses 1px `border` dividers between sections for blueprint structure.
- **Mobile:** margins shrink to 16px (`margin-mobile`), grids collapse to single stack.

## Elevation & Depth

No drop shadows. Depth comes from tonal stacking and outlines.

- **Dark mode — Tonal Stacking:** surface containers step lighter as they rise. Interactive elements use color shifts or 1px borders instead of shadows. 8px backdrop-blur on overlays and nav bars.
- **Light mode — Outlines + Tonal Layering:** surface containers step darker/greyer. 1px `border` tokens define separation. Raised elements use offset borders or secondary-blue tint shifts.
- **Interactivity:** focus and active states use high-contrast color shifts (e.g. primary to secondary blue), not z-axis movement.

## Shapes

**Technical and Precise** — soft, not bubbly.

- **Standard elements:** 4px radius (`rounded.DEFAULT`).
- **Large containers** (cards, modals, code blocks): 8px (`rounded.lg`).
- **Interactive triggers** (buttons, inputs): 4px for compact, technical look.

## Components

- **Buttons:** solid Deep Blue primary with white text; ghost-style secondary with 1px secondary-blue border. Labels use `label-caps` (monospaced).
- **Code Blocks:** always dark-surfaced regardless of page theme. Headers show language in `label-caps`.
- **Chips/Tags/Badges:** `label-caps`, all-caps, monospaced inside a subtle `*-container` tint.
- **Cards:** dark mode uses `Surface 2` fill with primary-blue 1px border on hover; light mode uses 1px `border` outline with darker header strip.
- **Inputs:** darker-than-surface fill in dark mode with primary-color bottom border expanding on focus; base-surface fill in light mode with `border` transitioning to secondary blue.
- **Lists:** horizontal separators; hover uses subtle background-tint shift.
- **Technical Readouts:** bordered box with `label-caps` label top-left, `code-inline` data points inside.
- **Reading Progress Bar:** thin 2px secondary-blue line at viewport top, fills on scroll.