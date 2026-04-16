/**
 * GitHub Trending Repositories Scraper
 *
 * OpenClaw Skill for scraping trending repos from GitHub
 */

module.exports = {
  name: "github-trending",
  description: "Get trending repositories from GitHub",
  version: "1.0.0",

  schema: {
    language: {
      type: "string",
      description: "Programming language filter (e.g., 'python', 'rust', 'javascript')",
      default: ""
    },
    timeframe: {
      type: "string",
      description: "Time period: 'daily', 'weekly', or 'monthly'",
      default: "daily",
      enum: ["daily", "weekly", "monthly"]
    },
    limit: {
      type: "number",
      description: "Maximum number of repos to return",
      default: 10,
      min: 1,
      max: 25
    }
  },

  async execute({ browser, args, logger }) {
    const { language = '', timeframe = 'daily', limit = 10 } = args;

    logger.info(`Fetching GitHub trending (${timeframe}, ${language || 'all languages'})...`);

    try {
      const page = await browser.newPage();

      // Build URL
      const languagePath = language ? `/${encodeURIComponent(language)}` : '';
      const url = `https://github.com/trending${languagePath}?since=${timeframe}`;

      logger.debug(`Navigating to: ${url}`);

      await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 20000
      });

      // Wait for content to load
      await page.waitForSelector('article.Box-row', { timeout: 10000 });

      // Extract repository data
      const repos = await page.evaluate((maxRepos) => {
        const items = [];
        const articles = document.querySelectorAll('article.Box-row');

        articles.forEach((article, idx) => {
          if (idx >= maxRepos) return;

          // Repository name and URL
          const titleElem = article.querySelector('h2 a');
          const repoName = titleElem?.textContent?.trim().replace(/\s+/g, '') || '';
          const repoUrl = titleElem?.getAttribute('href') || '';

          // Description
          const descElem = article.querySelector('p');
          const description = descElem?.textContent?.trim() || '';

          // Language
          const langElem = article.querySelector('[itemprop="programmingLanguage"]');
          const language = langElem?.textContent?.trim() || '';

          // Stars (total and today)
          const starElems = article.querySelectorAll('.octicon-star');
          let totalStars = '';
          let starsToday = '';

          starElems.forEach(elem => {
            const parent = elem.parentElement;
            const text = parent?.textContent?.trim() || '';

            if (text.includes('today')) {
              starsToday = text.replace('stars today', '').trim();
            } else {
              totalStars = text;
            }
          });

          // Forks
          const forkElem = article.querySelector('.octicon-repo-forked');
          const forks = forkElem?.parentElement?.textContent?.trim() || '';

          // Built by (contributors)
          const builtByElems = article.querySelectorAll('.avatar');
          const contributors = builtByElems.length;

          items.push({
            rank: idx + 1,
            name: repoName,
            url: repoUrl ? `https://github.com${repoUrl}` : '',
            description: description,
            language: language,
            stars: totalStars,
            stars_today: starsToday,
            forks: forks,
            contributors: contributors
          });
        });

        return items;
      }, limit);

      await page.close();

      logger.info(`Successfully scraped ${repos.length} trending repos`);

      return {
        success: true,
        data: repos,
        meta: {
          source: "github-trending",
          language: language || "all",
          timeframe: timeframe,
          scraped_at: new Date().toISOString(),
          count: repos.length
        }
      };

    } catch (error) {
      logger.error(`GitHub trending scraping failed: ${error.message}`);

      return {
        success: false,
        error: error.message,
        data: []
      };
    }
  }
};
