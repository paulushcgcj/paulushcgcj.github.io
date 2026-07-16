---
title: Blog Posts
permalink: /blog/
layout: article-list
description: Personal reflections, experiences, and thoughts from my journey through software development and life.
---

<div class="blog-page">
  {%- comment -%} Breadcrumb {%- endcomment -%}
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="{{ '/' | relative_url }}" class="breadcrumb__item">Home</a>
    <span class="breadcrumb__separator material-symbols-outlined" aria-hidden="true">chevron_right</span>
    <span class="breadcrumb__item breadcrumb__item--active">Blog</span>
  </nav>

  {%- comment -%} Page Header {%- endcomment -%}
  <header class="article-list-header">
    <h1 class="article-list-header__title">Blog</h1>
    {%- if page.description %}
    <p class="article-list-header__description">{{ page.description }}</p>
    {%- endif %}
  </header>

  {%- comment -%} Blog posts grouped by year {%- endcomment -%}
  {%- assign blog_posts = site.posts | where_exp: "item", "item.categories contains 'blog'" %}
  {%- assign postsByYear = blog_posts | group_by_exp: 'post', 'post.date | date: "%Y"' %}
  
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
