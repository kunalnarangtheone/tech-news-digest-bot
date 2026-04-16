/**
 * Daily Tech Digest Workflow
 *
 * Automatically generates and sends a daily tech digest
 * combining news from HackerNews, GitHub, and Dev.to
 *
 * Schedule: Every day at 9:00 AM
 * OpenClaw Cron: 0 9 * * *
 */

module.exports = {
  name: "daily-tech-digest",
  description: "Generate and send daily tech news digest",
  schedule: "0 9 * * *",

  async execute({ openclaw, telegram, storage }) {
    console.log(`[${new Date().toISOString()}] Starting daily tech digest...`);

    try {
      // 1. Gather data from all sources in parallel
      const [hnStories, ghRepos, devArticles] = await Promise.all([
        openclaw.executeSkill("hackernews-top-stories", { limit: 5 }),
        openclaw.executeSkill("github-trending", { timeframe: "daily" }),
        openclaw.executeSkill("devto-trending", { timeframe: "day" })
      ]);

      // 2. Format the digest
      const digest = formatDailyDigest({
        hackernews: hnStories.data || [],
        github: ghRepos.data || [],
        devto: devArticles.data || [],
        date: new Date().toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      });

      // 3. Send to configured Telegram channel
      const channelId = process.env.TELEGRAM_CHANNEL_ID || process.env.TELEGRAM_DIGEST_CHANNEL;

      if (!channelId) {
        console.error("TELEGRAM_CHANNEL_ID not configured");
        return { success: false, error: "Channel not configured" };
      }

      await telegram.sendMessage({
        chat_id: channelId,
        text: digest,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });

      // 4. Store digest metadata for analytics
      await storage.set(`digest-${Date.now()}`, {
        date: new Date().toISOString(),
        hn_count: hnStories.data?.length || 0,
        gh_count: ghRepos.data?.length || 0,
        dev_count: devArticles.data?.length || 0,
        sent: true
      });

      console.log("✅ Daily digest sent successfully!");
      return { success: true };

    } catch (error) {
      console.error("❌ Error generating daily digest:", error);
      return { success: false, error: error.message };
    }
  }
};

/**
 * Format aggregated data into a beautiful Telegram message
 */
function formatDailyDigest(data) {
  let digest = `📰 *Your Daily Tech Digest*\n${data.date}\n\n`;
  digest += `━━━━━━━━━━━━━━━━━━━━\n\n`;

  // HackerNews Section
  if (data.hackernews.length > 0) {
    digest += "🔥 *Top on HackerNews*\n\n";
    data.hackernews.slice(0, 5).forEach((story, idx) => {
      digest += `${idx + 1}\\. [${escapeMarkdown(story.title)}](${story.url})\n`;
      digest += `   _${story.score}_\n\n`;
    });
  }

  // GitHub Trending Section
  if (data.github.length > 0) {
    digest += "⭐ *GitHub Trending*\n\n";
    data.github.slice(0, 5).forEach((repo, idx) => {
      digest += `${idx + 1}\\. [${escapeMarkdown(repo.name)}](${repo.url})\n`;
      if (repo.description) {
        digest += `   ${escapeMarkdown(repo.description.substring(0, 100))}...\n`;
      }
      digest += `   ${repo.stars}\n\n`;
    });
  }

  // Dev.to Section
  if (data.devto.length > 0) {
    digest += "📝 *Trending Articles*\n\n";
    data.devto.slice(0, 5).forEach((article, idx) => {
      digest += `${idx + 1}\\. [${escapeMarkdown(article.title)}](${article.url})\n`;
      digest += `   _by ${escapeMarkdown(article.author)} • ${article.reactions}_\n\n`;
    });
  }

  digest += `━━━━━━━━━━━━━━━━━━━━\n`;
  digest += `\n🤖 _Powered by Tech Digest Bot_`;

  return digest;
}

/**
 * Escape markdown special characters for Telegram
 */
function escapeMarkdown(text) {
  if (!text) return '';
  return text.replace(/[_*[\]()~`>#+\-=|{}.!]/g, '\\$&');
}
