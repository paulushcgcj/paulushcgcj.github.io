---
layout: page
title: About
permalink: /about/
---

<style>
  /* ========================================================================
     ABOUT PAGE — Override page-layout constraints
     The page layout constrains to 720px. About page needs full container
     width for the hero and bento grid. Scoped to avoid affecting other pages.
     ======================================================================== */

  .page-layout {
    max-width: 100%;
    padding-block: 0;
  }

  .page-header {
    display: none;
  }

  .page-content.article {
    max-width: 100%;
    margin: 0;
    padding: 0;
    border: none;
  }

  .article__content {
    max-width: 100%;
    margin: 0;
    padding: 0;
  }

  /* ========================================================================
     GRID PATTERN BACKGROUND
     Subtle 40px grid lines, adapted from Stitch design
     ======================================================================== */

  .about-grid-pattern {
    background-image:
      linear-gradient(to right, rgba(0, 0, 0, 0.03) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  [data-theme="dark"] .about-grid-pattern {
    background-image:
      linear-gradient(to right, rgba(139, 145, 156, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(139, 145, 156, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  /* ========================================================================
     ABOUT PAGE — Hero Section
     ======================================================================== */

  .about-hero {
    padding-top: 80px; /* nav height */
    padding-bottom: var(--space-3xl);
    padding-left: var(--space-lg);
    padding-right: var(--space-lg);
  }

  .about-hero__inner {
    max-width: var(--container-max);
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: var(--space-3xl);
    align-items: flex-start;
  }

  @media (min-width: 768px) {
    .about-hero__inner {
      flex-direction: row;
      gap: var(--space-3xl);
    }
  }

  .about-hero__content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--space-lg);
  }

  .about-hero__heading {
    font-family: var(--font-display);
    font-size: clamp(32px, 5vw, var(--font-size-display-lg));
    line-height: var(--line-height-display-lg);
    font-weight: 700;
    letter-spacing: var(--letter-spacing-display-lg);
    color: var(--color-on-primary-fixed);
    margin: 0;
  }

  [data-theme="dark"] .about-hero__heading {
    color: var(--color-primary);
  }

  .about-hero__role {
    display: inline-block;
    width: fit-content;
    background-color: rgba(30, 78, 140, 0.1);
    border-left: 4px solid var(--color-secondary);
    padding: var(--space-xs) var(--space-md);
  }

  [data-theme="dark"] .about-hero__role {
    background-color: rgba(168, 200, 255, 0.08);
    border-left-color: var(--color-primary);
  }

  .about-hero__role-text {
    font: var(--text-label-caps);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--color-secondary);
    margin: 0;
  }

  [data-theme="dark"] .about-hero__role-text {
    color: var(--color-primary);
  }

  .about-hero__bio {
    font: var(--text-article-body);
    letter-spacing: var(--letter-spacing-article-body);
    color: var(--color-on-surface);
    max-width: var(--article-max);
    margin: 0;
  }

  .about-hero__links {
    display: flex;
    gap: var(--space-md);
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .about-hero__link {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-md);
    border: var(--border-width-default) solid var(--color-outline-variant);
    background-color: var(--color-surface-container-lowest);
    color: var(--color-on-surface-variant);
    text-decoration: none;
    transition: border-color var(--transition-fast),
                background-color var(--transition-fast),
                color var(--transition-fast);
  }

  .about-hero__link:hover {
    border-color: var(--color-secondary);
    background-color: rgba(184, 92, 62, 0.05);
    color: var(--color-secondary);
  }

  [data-theme="dark"] .about-hero__link:hover {
    border-color: var(--color-primary);
    background-color: rgba(168, 200, 255, 0.05);
    color: var(--color-primary);
  }

  .about-hero__link .material-symbols-outlined {
    font-size: 20px;
  }

  /* Logo / Brand Image */
  .about-hero__image {
    width: 100%;
    max-width: 320px;
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-surface-container-low);
    border: var(--border-width-default) solid var(--color-outline-variant);
    position: relative;
    overflow: hidden;
    padding: var(--space-xl);
    flex-shrink: 0;
  }

  @media (min-width: 768px) {
    .about-hero__image {
      width: 33%;
      max-width: none;
    }
  }

  .about-hero__image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: grayscale(1);
    opacity: 0.9;
    transition: filter 700ms ease, opacity 700ms ease;
  }

  .about-hero__image:hover img {
    filter: grayscale(0);
    opacity: 1;
  }

  .about-hero__image-frame {
    position: absolute;
    inset: 0;
    border: 12px solid var(--color-surface-container-low);
    pointer-events: none;
  }

  .about-hero__image-badge {
    position: absolute;
    top: var(--space-md);
    right: var(--space-md);
    background-color: var(--color-on-primary-fixed);
    color: var(--color-surface-container-lowest);
    padding: var(--space-xs) var(--space-sm);
    font: var(--text-label-caps);
    letter-spacing: var(--letter-spacing-label-caps);
    text-transform: uppercase;
  }

  [data-theme="dark"] .about-hero__image-badge {
    background-color: var(--color-primary);
    color: var(--color-on-primary);
  }

  /* ========================================================================
     ABOUT PAGE — Bento Grid
     ======================================================================== */

  .about-bento {
    padding: 0 var(--space-lg) var(--space-4xl);
  }

  .about-bento__inner {
    max-width: var(--container-max);
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }

  @media (min-width: 768px) {
    .about-bento__inner {
      grid-template-columns: repeat(12, 1fr);
    }
  }

  /* --- Tech Stack Panel --- */

  .about-tech {
    background-color: var(--color-surface-container-lowest);
    border: var(--border-width-default) solid var(--color-outline-variant);
    border-left: 6px solid var(--color-secondary);
    padding: var(--space-xl);
    position: relative;
  }

  [data-theme="dark"] .about-tech {
    border-left-color: var(--color-primary);
  }

  @media (min-width: 768px) {
    .about-tech {
      grid-column: span 8;
    }
  }

  .about-tech__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-xl);
  }

  .about-tech__title {
    font: var(--text-headline-md);
    color: var(--color-on-primary-fixed);
    margin: 0;
  }

  [data-theme="dark"] .about-tech__title {
    color: var(--color-primary);
  }

  .about-tech__version {
    font: var(--text-label-caps);
    color: var(--color-outline);
    font-style: italic;
  }

  .about-tech__cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-md);
  }

  @media (min-width: 640px) {
    .about-tech__cards {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .about-tech-card {
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
    padding: var(--space-lg);
    background-color: var(--color-surface-container-low);
    border: var(--border-width-default) solid var(--color-outline-variant);
    transition: border-color var(--transition-fast),
                background-color var(--transition-fast);
  }

  .about-tech-card:hover {
    border-color: var(--color-secondary);
    background-color: var(--color-surface-bright);
  }

  [data-theme="dark"] .about-tech-card:hover {
    border-color: var(--color-primary);
  }

  .about-tech-card .material-symbols-outlined {
    color: var(--color-secondary);
    font-size: 24px;
  }

  [data-theme="dark"] .about-tech-card .material-symbols-outlined {
    color: var(--color-primary);
  }

  .about-tech-card__label {
    font: var(--text-label-caps);
    letter-spacing: var(--letter-spacing-label-caps);
    text-transform: uppercase;
    color: var(--color-on-primary-fixed);
    margin: 0;
  }

  [data-theme="dark"] .about-tech-card__label {
    color: var(--color-on-surface);
  }

  .about-tech__description {
    margin-top: var(--space-xl);
    font: var(--text-article-body);
    color: var(--color-on-surface-variant);
    max-width: 60ch;
  }

  /* --- Interests Panel --- */

  .about-interests {
    background-color: var(--color-surface-container);
    border: var(--border-width-default) solid var(--color-outline-variant);
    border-top: 6px solid var(--color-secondary);
    padding: var(--space-xl);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  [data-theme="dark"] .about-interests {
    background-color: var(--color-surface-container-highest);
    border-top-color: var(--color-primary);
  }

  @media (min-width: 768px) {
    .about-interests {
      grid-column: span 4;
    }
  }

  .about-interests__title {
    font: var(--text-headline-md);
    color: var(--color-secondary);
    margin: 0 0 var(--space-lg) 0;
  }

  [data-theme="dark"] .about-interests__title {
    color: var(--color-secondary);
  }

  .about-interests__list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
  }

  .about-interests__item {
    display: flex;
    align-items: center;
    gap: var(--space-md);
  }

  .about-interests__dot {
    width: 6px;
    height: 6px;
    flex-shrink: 0;
    background-color: var(--color-secondary);
  }

  [data-theme="dark"] .about-interests__dot {
    background-color: var(--color-primary);
  }

  .about-interests__label {
    font: var(--text-label-caps);
    letter-spacing: var(--letter-spacing-label-caps);
    text-transform: uppercase;
    color: var(--color-on-surface);
    margin: 0;
  }

  .about-interests__quote {
    margin-top: var(--space-3xl);
    padding-top: var(--space-lg);
    border-top: var(--border-width-default) solid var(--color-outline-variant);
  }

  .about-interests__quote p {
    font: var(--text-code-inline);
    color: var(--color-on-surface-variant);
    font-style: italic;
    margin: 0;
  }
</style>

<!-- ================================================================
     ABOUT PAGE CONTENT — Hero + Bento Grid
     Matches Stitch design: about_paulo_cruz_light_mode.html
     Uses CSS custom properties for automatic light/dark mode
     ================================================================ -->

<div class="about-grid-pattern">

  <!-- Hero Section -->
  <section class="about-hero" aria-label="About Paulo Cruz">
    <div class="about-hero__inner">

      <div class="about-hero__content">
        <h1 class="about-hero__heading">PAULO CRUZ</h1>

        <div class="about-hero__role">
          <p class="about-hero__role-text">Software Architect &amp; Tech Lead</p>
        </div>

        <p class="about-hero__bio">
          I'm a seasoned software developer, DevOps enthusiast, and avid learner
          based in Victoria, BC. Born and raised in São Paulo, Brazil, I bring a
          unique blend of creativity and discipline to building robust digital
          architectures. My work focuses on high-performance Java systems,
          PostgreSQL encryption, and scalable Spring Boot applications.
        </p>

        <ul class="about-hero__links" role="list">
          <li>
            <a href="https://terminal.paulushcgcj.github.io/"
               class="about-hero__link"
               aria-label="Terminal Profile"
               target="_blank"
               rel="noopener noreferrer">
              <span class="material-symbols-outlined" aria-hidden="true">terminal</span>
            </a>
          </li>
          <li>
            <a href="https://github.com/paulushcgcj"
               class="about-hero__link"
               aria-label="GitHub Profile"
               target="_blank"
               rel="noopener noreferrer">
              <span class="material-symbols-outlined" aria-hidden="true">hub</span>
            </a>
          </li>
          <li>
            <a href="mailto:paulushc@gmail.com"
               class="about-hero__link"
               aria-label="Email Contact">
              <span class="material-symbols-outlined" aria-hidden="true">alternate_email</span>
            </a>
          </li>
        </ul>
      </div>

      <div class="about-hero__image" role="img" aria-label="Paulo Cruz brand icon">
        <img alt="Paulo Cruz brand icon"
             src="/assets/icon88x88.png">
        <div class="about-hero__image-frame" aria-hidden="true"></div>
        <div class="about-hero__image-badge">
          <span class="sr-only">Status: </span>ACTIVE
        </div>
      </div>

    </div>
  </section>

  <!-- Bento Grid: Tech Stack & Interests -->
  <div class="about-bento" aria-label="Skills and interests">
    <div class="about-bento__inner">

      <!-- Tech Stack -->
      <div class="about-tech">
        <div class="about-tech__header">
          <h2 class="about-tech__title">CORE_SYSTEMS</h2>
          <span class="about-tech__version">V_05.1</span>
        </div>

        <div class="about-tech__cards">
          <div class="about-tech-card">
            <span class="material-symbols-outlined" aria-hidden="true">coffee</span>
            <span class="about-tech-card__label">JAVA / SPRING</span>
          </div>
          <div class="about-tech-card">
            <span class="material-symbols-outlined" aria-hidden="true">database</span>
            <span class="about-tech-card__label">POSTGRESQL</span>
          </div>
          <div class="about-tech-card">
            <span class="material-symbols-outlined" aria-hidden="true">encrypted</span>
            <span class="about-tech-card__label">SECURITY</span>
          </div>
          <div class="about-tech-card">
            <span class="material-symbols-outlined" aria-hidden="true">settings_suggest</span>
            <span class="about-tech-card__label">DEVOPS / LINUX</span>
          </div>
        </div>

        <p class="about-tech__description">
          Specializing in multi-database environments and data encryption.
          Currently exploring advanced column-level encryption and secure
          connection protocols in the digital landscape.
        </p>
      </div>

      <!-- Interests -->
      <div class="about-interests">
        <div>
          <h2 class="about-interests__title">PROJECT_LOG</h2>
          <ul class="about-interests__list" role="list">
            <li class="about-interests__item">
              <span class="about-interests__dot" aria-hidden="true"></span>
              <span class="about-interests__label">Software Development</span>
            </li>
            <li class="about-interests__item">
              <span class="about-interests__dot" aria-hidden="true"></span>
              <span class="about-interests__label">DevOps Engineering</span>
            </li>
            <li class="about-interests__item">
              <span class="about-interests__dot" aria-hidden="true"></span>
              <span class="about-interests__label">Problem Solving</span>
            </li>
            <li class="about-interests__item">
              <span class="about-interests__dot" aria-hidden="true"></span>
              <span class="about-interests__label">Continuous Learning</span>
            </li>
          </ul>
        </div>

        <div class="about-interests__quote">
          <p>"The artifact of my crazy mind."</p>
        </div>
      </div>

    </div>
  </div>

</div>
