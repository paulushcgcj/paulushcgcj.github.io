---
title: Wolfpack Games
permalink: /wolfpack/
layout: article-list
description: The family "business" of making games for fun — adventures in game development with MonoGame and C#.
---

<div class="wolfpack-page">
  {%- comment -%} Breadcrumb {%- endcomment -%}
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="{{ '/' | relative_url }}" class="breadcrumb__item">Home</a>
    <span class="breadcrumb__separator material-symbols-outlined" aria-hidden="true">chevron_right</span>
    <span class="breadcrumb__item breadcrumb__item--active">Wolfpack</span>
  </nav>

  {%- comment -%} Page Header {%- endcomment -%}
  <header class="article-list-header">
    <h1 class="article-list-header__title">Wolfpack</h1>
    {%- if page.description %}
    <p class="article-list-header__description">{{ page.description }}</p>
    {%- endif %}
  </header>

  {%- comment -%} Games grouped by year {%- endcomment -%}
  {%- assign games = site.posts | where_exp: "item", "item.categories contains 'game'" %}
  {%- assign postsByYear = games | group_by_exp: 'post', 'post.date | date: "%Y"' %}
  
  <div class="article-list">
    {%- for year in postsByYear %}
    <div class="article-list__year-group">
      <aside class="article-list__year-sidebar">
        <div class="article-list__year-sticky">
          <h2 class="article-list__year-label">{{ year.name }}</h2>
          <span class="article-list__year-count">{{ year.items | size }} {% if year.items.size == 1 %}Entry{% else %}Entries{% endif %}</span>
        </div>
      </aside>
      
      <div class="article-list__items">
        {%- for post in year.items %}
          {%- include article-list-item.html post=post %}
        {%- endfor %}
      </div>
    </div>
    {%- endfor %}
  </div>
</div>
