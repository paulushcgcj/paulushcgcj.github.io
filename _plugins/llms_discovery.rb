# frozen_string_literal: true

# AI-agent discoverability generator.
#
# 1. Exposes each published post's raw Markdown source (front matter stripped)
#    as `raw_content`, so Liquid templates can emit machine-readable Markdown
#    instead of HTML-converted content.
# 2. Generates one machine-readable Markdown representation per post at
#    `<post-url>.md` (e.g. /articles/topic.html -> /articles/topic.md),
#    rendered through the pure-Liquid layout `_layouts/article-markdown.txt`.
#
# Drafts are never touched: site.posts only contains documents from _posts/.
# Uses Jekyll core APIs only; no additional gems required.

module LlmsDiscovery
  FRONT_MATTER_RE = /\A---\r?\n.*?\r?\n---\r?\n?/m.freeze

  class Generator < Jekyll::Generator
    priority :low

    def generate(site)
      return unless site.posts

      site.posts.docs.each do |post|
        raw = raw_source(site, post)
        next unless raw

        post.data['raw_content'] = raw.sub(FRONT_MATTER_RE, '').strip

        md_url = "#{post.url.delete_suffix('.html')}.md"
        site.pages << markdown_twin_page(site, post, md_url)
      end

      site.pages << generated_text_page(site, '/llms.txt', 'llms-index')
      site.pages << generated_text_page(site, '/llms-full.txt', 'llms-full')
    end

    private

    def raw_source(site, post)
      File.read(File.join(site.source, post.relative_path), mode: 'r:BOM|UTF-8')
    rescue StandardError => e
      Jekyll.logger.warn("llms_discovery: could not read #{post.relative_path}: #{e.message}")
      nil
    end

    def markdown_twin_page(site, post, url)
      page = Jekyll::PageWithoutAFile.new(site, site.source, '', 'index.txt')
      page.content = ' '
      page.data.merge!(
        'permalink' => url,
        'layout' => 'article-markdown',
        'sitemap' => false,
        'title' => "#{post.data['title']} (machine-readable Markdown)",
        'post' => post
      )
      page
    end

    def generated_text_page(site, url, layout)
      page = Jekyll::PageWithoutAFile.new(site, site.source, '', 'index.txt')
      page.content = ' '
      page.data.merge!(
        'permalink' => url,
        'layout' => layout,
        'sitemap' => false,
        'title' => 'AI discovery resource'
      )
      page
    end
  end
end
