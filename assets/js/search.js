/**
 * Search functionality for the blog.
 * Uses Fuse.js for fuzzy search on a pre-built JSON index.
 */
(function () {
  'use strict';

  var resultsContainer = document.getElementById('search-hits');
  var queryDisplay = document.getElementById('search-query');
  var emptyState = document.getElementById('search-empty');
  var loadingState = document.getElementById('search-loading');

  if (!resultsContainer || !queryDisplay) {
    return;
  }

  var params = new URLSearchParams(window.location.search);
  var query = params.get('q');

  if (!query || query.trim() === '') {
    loadingState.hidden = true;
    queryDisplay.textContent = 'Enter a search term in the navigation bar above.';
    return;
  }

  queryDisplay.textContent = 'Showing results for: "' + query + '"';

  fetch('/search-index.json')
    .then(function (response) {
      if (!response.ok) {
        throw new Error('Failed to load search index');
      }
      return response.json();
    })
    .then(function (posts) {
      loadingState.hidden = true;

      var fuse = new Fuse(posts, {
        keys: [
          { name: 'title', weight: 0.4 },
          { name: 'categories', weight: 0.2 },
          { name: 'excerpt', weight: 0.2 },
          { name: 'content', weight: 0.2 }
        ],
        threshold: 0.3,
        includeMatches: true,
        includeScore: true,
        limit: 20
      });

      var results = fuse.search(query);

      if (results.length === 0) {
        emptyState.hidden = false;
        return;
      }

      queryDisplay.textContent = 'Showing ' + results.length + ' result' + (results.length === 1 ? '' : 's') + ' for: "' + query + '"';

      resultsContainer.innerHTML = results.map(function (result) {
        var item = result.item;
        var date = new Date(item.date);
        var formattedDate = date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
        var categories = item.categories.map(function (cat) {
          return '<span class="search-hit__category">' + escapeHtml(cat) + '</span>';
        }).join(' ');

        return '<article class="search-hit">' +
          '<h2 class="search-hit__title"><a href="' + item.url + '">' + escapeHtml(item.title) + '</a></h2>' +
          '<div class="search-hit__meta">' +
            '<time class="search-hit__date" datetime="' + item.date + '">' + formattedDate + '</time>' +
            '<span class="search-hit__categories">' + categories + '</span>' +
          '</div>' +
          '<p class="search-hit__excerpt">' + escapeHtml(item.excerpt) + '</p>' +
        '</article>';
      }).join('');
    })
    .catch(function (error) {
      loadingState.hidden = true;
      queryDisplay.textContent = 'Error loading search index. Please try again later.';
      console.error('Search error:', error);
    });

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }
})();
