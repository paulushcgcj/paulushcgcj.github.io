# AGENTS.md — paulushcgcj.github.io

## Project Overview

Personal Jekyll blog and portfolio site for Paulo Cruz. Jekyll 4.3.3, Ruby-based, hosted on GitHub Pages.

## Quick Commands

```bash
bundle exec jekyll serve    # Local dev server (http://localhost:4000)
bundle exec jekyll build    # Build site to _site/
bundle update               # Update dependencies
```

## Repository Structure

- `_posts/` — Blog articles and Wolfpack game posts (Markdown with front matter)
- `_layouts/` — HTML layout templates (default, page, post, home, cv)
- `_includes/` — Reusable HTML partials (header, footer, nav, head, bibliography)
- `_sass/` — SCSS partials (tokens → themes → base → components → templates → utilities)
- `pages/` — Static pages (about, CV, articles index, blog index, wolfpack)
- `_data/` — YAML data files (navigation.yml, authors.yml)
- `_bibliography/` — Per-post BibTeX files (`<slug>.bib`) for jekyll-scholar
- `assets/` — Static assets organized by year and type
- `DESIGN.md` — Design system tokens (colors, typography, spacing, shapes) used by Stitch

## SCSS Architecture

Import order in `assets/css/main.scss` is critical:
1. `_tokens.scss` — CSS custom properties for colors, typography, spacing
2. `_themes.scss` — Light/dark mode assignments via `[data-theme="dark"]`
3. `_base.scss` — Element resets and typographic defaults
4. `_components.scss` — BEM component styles
5. `_templates.scss` — Layout and template-specific styles
6. `_utilities.scss` — Single-property helper classes

All design tokens derive from `DESIGN.md`. Naming: `--color-*`, `--font-*`, `--text-*`, `--space-*`, `--radius-*`.

## Post Front Matter

Required fields:
```yaml
---
title: "Post Title"
date: YYYY-MM-DD HH:MM:SS -0700
categories: [tag1, tag2]
author: paulushc
license: CC-BY-4.0
permalink: /category/post-slug
header:
    teaser: /assets/YYYY/MM/type/image-name.jpg
    overlay_image: /assets/YYYY/MM/type/image-name.jpg
    overlay_filter: 0.5
    show_overlay_excerpt: false
---
```

### Scholar-aware front matter (academic references)

When a post cites academic works (papers, books, proceedings), use jekyll-scholar:
```yaml
---
has_bibliography: true
scholar:
  bibliography: <slug>
resources:
  - title: "Non-academic resource (repo, tool, blog)"
    url: "https://example.com"
    icon: "link"
---
```

- `_bibliography/<slug>.bib` holds the BibTeX entries (one file per post).
- Inline citations use `{% cite <key> %}` (renders as `(Author, Year)`).
- Academic references go to the bibliography; non-academic ones go to the sidebar `resources:` block.

## Content Categories

- **articles/** — Technical articles (Java, PostgreSQL, Spring Boot, security)
- **blog/** — Personal blog posts
- **wolfpack/** — Game development posts (MonoGame, C#)

## License Convention

All original content uses `CC-BY-4.0`. The `_includes/cc-by-4.0-footer.html` partial renders license attribution when `license` is set in front matter.

## Navigation

`_data/navigation.yml` controls the main nav. Pages in `pages/` use `layout: page` and are linked from there.

## Gotchas

- Dev container uses `mcr.microsoft.com/devcontainers/jekyll:2-bullseye` (Ruby, not Node)
- `_drafts/` is gitignored — drafts live here until published
- `future: true` is set in `_config.yml` — scheduled/future-dated posts build normally
- `stitch_screens/` is gitignored — Stitch design tool output
- `.playwright-mcp/` is gitignored
- `vendor/` and `.bundle/` are gitignored — run `bundle install` after clone
- Posts use `<!--more-->` for excerpt separators
- The about page has custom inline CSS overriding page layout constraints
- CSS custom properties enable runtime theme switching (no build-time dark/light split)
- jekyll-scholar requires a `_bibliography/references.bib` stub even when all posts use
  per-post `.bib` overrides (the gem initializes from the default path)
