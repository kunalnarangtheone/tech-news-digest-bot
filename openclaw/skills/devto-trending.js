/**
 * Dev.to Trending Articles Scraper
 *
 * OpenClaw Skill for scraping trending articles from Dev.to
 */

module.exports = {
  name: "devto-trending",
  description: "Get trending articles from Dev.to",
  version: "1.0.0",

  schema: {
    tag: {
      type: "string",
      description: "Topic tag filter (e.g., 'python', 'webdev', 'javascript')",
      default: ""
    },
    timeframe: {
      type: "string",
      description: "Time period: 'day', 'week', 'month', 'year', 'infinity'",
      default: "week",
      enum: ["day", "week", "month", "year", "infinity"]
    },
    limit: {
      type: "number",
      description: "Maximum number of articles to return",
      default: 10,
      min: 1,
      max: 20
    }
  },

  async execute({ browser, args, logger }) {
    const { tag = '', timeframe = 'week', limit = 10 } = args;

    logger.info(`Fetching Dev.to trending (${timeframe}${tag ? `, tag: ${tag}` : ''})...`);

    try {
      const page = await browser.newPage();

      // Build URL
      const url = tag
        ? `https://dev.to/t/${encodeURIComponent(tag)}/top/${timeframe}`
        : `https://dev.to/top/${timeframe}`;

      logger.debug(`Navigating to: ${url}`);

      await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 20000
      });

      // Wait for articles to load
      await page.waitForSelector('article.crayons-story, div.crayons-story', { timeout: 10000 });

      // Extract article data
      const articles = await page.evaluate((maxArticles) => {
        const items = [];
        const posts = document.querySelectorAll('article.crayons-story, div.crayons-story');

        posts.forEach((post, idx) => {
          if (idx >= maxArticles) return;

          // Title and URL
          const titleElem = post.querySelector('h2 a, h3 a');
          const title = titleElem?.textContent?.trim() || '';
          const url = titleElem?.getAttribute('href') || '';

          // Author
          const authorElem = post.querySelector('.crayons-story__secondary .crayons-link, .profile-preview-card__trigger');
          const author = authorElem?.textContent?.trim() || '';

          // Tags
          const tagElems = post.querySelectorAll('.crayons-tag');
          const tags = Array.from(tagElems).map(t => t.textContent.trim().replace('#', ''));

          // Reactions (likes/hearts)
          const reactionsElem = post.querySelector('.aggregate_reactions_counter');
          const reactions = reactionsElem?.textContent?.trim() || '0';

          // Comments count
          const commentsElem = post.querySelector('.crayons-story__engagement a[href*="comments"]');
          const comments = commentsElem?.textContent?.trim()?.match(/\d+/)?.[0] || '0';

          // Reading time
          const readTimeElem = post.querySelector('.crayons-story__tertiary small');
          const readTime = readTimeElem?.textContent?.trim() || '';

          // Published date
          const dateElem = post.querySelector('time');
          const publishedDate = dateElem?.getAttribute('datetime') || '';

          // Snippet/preview
          const snippetElem = post.querySelector('.crayons-story__snippet, .crayons-story__description');
          const snippet = snippetElem?.textContent?.trim() || '';

          items.push({
            rank: idx + 1,
            title: title,
            url: url.startsWith('http') ? url : `https://dev.to${url}`,
            author: author,
            tags: tags,
            reactions: reactions,
            comments: comments,
            read_time: readTime,
            published_date: publishedDate,
            snippet: snippet.substring(0, 150)
          });
        });

        return items;
      }, limit);

      await page.close();

      logger.info(`Successfully scraped ${articles.length} articles`);

      return {
        success: true,
        data: articles,
        meta: {
          source: "devto",
          tag: tag || "all",
          timeframe: timeframe,
          scraped_at: new Date().toISOString(),
          count: articles.length
        }
      };

    } catch (error) {
      logger.error(`Dev.to scraping failed: ${error.message}`);

      return {
        success: false,
        error: error.message,
        data: []
      };
    }
  }
};
