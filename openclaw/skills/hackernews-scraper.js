/**
 * HackerNews Top Stories Scraper
 *
 * OpenClaw Skill for scraping top stories from HackerNews
 * Uses browser automation via CDP protocol
 */

module.exports = {
  name: "hackernews-top-stories",
  description: "Scrape top stories from HackerNews frontpage",
  version: "1.0.0",

  // Skill parameters schema
  schema: {
    limit: {
      type: "number",
      description: "Maximum number of stories to retrieve",
      default: 10,
      min: 1,
      max: 30
    }
  },

  async execute({ browser, args, logger }) {
    const { limit = 10 } = args;

    logger.info(`Fetching top ${limit} HackerNews stories...`);

    try {
      // Create new browser page
      const page = await browser.newPage();

      // Set user agent to avoid detection
      await page.setUserAgent(
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      );

      // Navigate to HackerNews
      await page.goto('https://news.ycombinator.com', {
        waitUntil: 'networkidle2',
        timeout: 15000
      });

      // Extract story data
      const stories = await page.evaluate((maxStories) => {
        const items = [];
        const storyRows = document.querySelectorAll('.athing');

        for (let i = 0; i < Math.min(maxStories, storyRows.length); i++) {
          const row = storyRows[i];
          const titleLine = row.querySelector('.titleline > a');
          const scoreRow = row.nextElementSibling;
          const scoreElem = scoreRow?.querySelector('.score');
          const ageElem = scoreRow?.querySelector('.age');
          const commentsElem = scoreRow?.querySelectorAll('a')[2];

          // Extract domain
          const siteStr = row.querySelector('.sitestr');

          items.push({
            rank: i + 1,
            title: titleLine?.textContent?.trim() || '',
            url: titleLine?.href || '',
            domain: siteStr?.textContent?.trim() || '',
            score: scoreElem?.textContent?.replace(' points', '') || '0',
            age: ageElem?.textContent?.trim() || '',
            comments: commentsElem?.textContent?.trim() || '0 comments',
            hn_url: `https://news.ycombinator.com/item?id=${row.id}`
          });
        }

        return items;
      }, limit);

      await page.close();

      logger.info(`Successfully scraped ${stories.length} stories`);

      return {
        success: true,
        data: stories,
        meta: {
          source: "hackernews",
          scraped_at: new Date().toISOString(),
          count: stories.length
        }
      };

    } catch (error) {
      logger.error(`HackerNews scraping failed: ${error.message}`);

      return {
        success: false,
        error: error.message,
        data: []
      };
    }
  }
};
