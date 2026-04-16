/**
 * Topic Monitoring Workflow
 *
 * Monitors specific tech topics and sends alerts when
 * significant discussions or projects emerge
 *
 * Schedule: Every 6 hours
 * OpenClaw Cron: 0 */6 * * *
 */

module.exports = {
  name: "topic-monitoring",
  description: "Monitor tech topics for trending discussions",
  schedule: "0 */6 * * *",

  // Topics to monitor - customize this list
  topics: [
    { name: "rust", keywords: ["rust", "rustlang", "cargo"] },
    { name: "webassembly", keywords: ["webassembly", "wasm", "wasmtime"] },
    { name: "kubernetes", keywords: ["kubernetes", "k8s", "kubectl"] },
    { name: "ai", keywords: ["artificial intelligence", "machine learning", "llm", "gpt"] },
    { name: "react", keywords: ["react", "reactjs", "nextjs"] },
    { name: "python", keywords: ["python", "python3", "pythonic"] }
  ],

  async execute({ openclaw, telegram, storage }) {
    console.log(`[${new Date().toISOString()}] Starting topic monitoring...`);

    const alerts = [];

    for (const topic of this.topics) {
      try {
        // Get latest HackerNews stories
        const hnResult = await openclaw.executeSkill("hackernews-top-stories", { limit: 30 });
        const stories = hnResult.data || [];

        // Filter stories matching topic keywords
        const matches = stories.filter(story => {
          const titleLower = story.title.toLowerCase();
          return topic.keywords.some(keyword => titleLower.includes(keyword.toLowerCase()));
        });

        if (matches.length === 0) continue;

        // Get previously seen stories for this topic
        const lastSeenKey = `monitor-${topic.name}-last-seen`;
        const lastSeen = await storage.get(lastSeenKey) || [];

        // Find new stories (not seen before)
        const newStories = matches.filter(story =>
          !lastSeen.includes(story.url) && parseInt(story.score) > 50
        );

        if (newStories.length > 0) {
          // Create alert for new trending discussions
          alerts.push({
            topic: topic.name,
            stories: newStories,
            total: matches.length
          });

          // Update storage with new URLs
          const updatedSeen = [...new Set([...lastSeen, ...matches.map(s => s.url)])];
          // Keep only last 100 URLs to prevent storage bloat
          await storage.set(lastSeenKey, updatedSeen.slice(-100));

          console.log(`📍 Found ${newStories.length} new ${topic.name} stories`);
        }

        // Also check GitHub trending
        const ghResult = await openclaw.executeSkill("github-trending", {
          language: topic.name === "python" ? "python" : "",
          timeframe: "daily"
        });

        const repos = ghResult.data || [];
        const relevantRepos = repos.filter(repo => {
          const searchText = `${repo.name} ${repo.description}`.toLowerCase();
          return topic.keywords.some(kw => searchText.includes(kw.toLowerCase()));
        });

        if (relevantRepos.length > 0) {
          const ghSeenKey = `monitor-${topic.name}-gh-seen`;
          const ghLastSeen = await storage.get(ghSeenKey) || [];
          const newRepos = relevantRepos.filter(repo => !ghLastSeen.includes(repo.url));

          if (newRepos.length > 0) {
            alerts.push({
              topic: topic.name,
              repos: newRepos,
              type: "github"
            });

            await storage.set(ghSeenKey, [...ghLastSeen, ...relevantRepos.map(r => r.url)].slice(-50));
          }
        }

      } catch (error) {
        console.error(`Error monitoring topic ${topic.name}:`, error);
      }
    }

    // Send alerts if any were generated
    if (alerts.length > 0) {
      const alertMessage = formatAlerts(alerts);
      const alertChatId = process.env.TELEGRAM_ALERT_CHAT || process.env.TELEGRAM_BOT_TOKEN;

      await telegram.sendMessage({
        chat_id: alertChatId,
        text: alertMessage,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });

      console.log(`✅ Sent ${alerts.length} topic alerts`);
    } else {
      console.log("No new trending topics to report");
    }

    return { success: true, alerts: alerts.length };
  }
};

/**
 * Format topic alerts into a Telegram message
 */
function formatAlerts(alerts) {
  let message = `🚨 *Trending Topic Alerts*\n\n`;

  for (const alert of alerts) {
    const topicEmoji = getTopicEmoji(alert.topic);

    if (alert.stories) {
      message += `${topicEmoji} *${capitalize(alert.topic)}* is trending on HackerNews!\n\n`;

      alert.stories.slice(0, 3).forEach(story => {
        message += `• [${escapeMarkdown(story.title)}](${story.url})\n`;
        message += `  _${story.score}_\n`;
      });

      message += `\n`;
    }

    if (alert.repos) {
      message += `${topicEmoji} *${capitalize(alert.topic)}* trending on GitHub!\n\n`;

      alert.repos.slice(0, 3).forEach(repo => {
        message += `⭐ [${escapeMarkdown(repo.name)}](${repo.url})\n`;
        if (repo.description) {
          message += `   _${escapeMarkdown(repo.description.substring(0, 80))}..._\n`;
        }
      });

      message += `\n`;
    }
  }

  message += `_Monitored at ${new Date().toLocaleTimeString()}_`;

  return message;
}

/**
 * Get emoji for topic
 */
function getTopicEmoji(topic) {
  const emojis = {
    rust: "🦀",
    webassembly: "⚙️",
    kubernetes: "☸️",
    ai: "🤖",
    react: "⚛️",
    python: "🐍",
    default: "🔥"
  };

  return emojis[topic] || emojis.default;
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Escape markdown special characters
 */
function escapeMarkdown(text) {
  if (!text) return '';
  return text.replace(/[_*[\]()~`>#+\-=|{}.!]/g, '\\$&');
}
