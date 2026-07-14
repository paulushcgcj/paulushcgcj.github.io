source "https://rubygems.org"

gem "jekyll", "~> 4.3.3"

# Force a newer sass-embedded version to fix Ruby 3.3 build errors
gem "sass-embedded", ">= 1.77.0"

# If you want to use GitHub Pages, remove the "gem "jekyll"" above and
# uncomment the line below. To upgrade, run `bundle update github-pages`.
# gem "github-pages", group: :jekyll_plugins

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-gist"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
end

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 2.0"
  gem "tzinfo-data"
end

gem "http_parser.rb", "~> 0.8.0", platforms: [:jruby]

gem "minimal-mistakes-jekyll", ">= 4.25.1"
gem "faraday-retry"