# AI Content Beast

Autonomous AI marketing agent that generates, optimizes, and posts aggressive AI content across 6 major social platforms — fully automated, running on GitHub Actions.

## What It Does

| Feature | Details |
|---|---|
| **Content Generation** | Creates original, aggressive AI marketing content every 4 hours using GPT-4 |
| **YouTube Monitoring** | Scrapes @theAIsearch channel every 2 hours for new videos, generates supporting content |
| **Multi-Platform Posting** | Auto-posts optimized versions to X, Instagram, Facebook, LinkedIn, Reddit, Telegram |
| **Auto-Reply** | Replies to comments on Twitter, Reddit, and Telegram every 30 minutes |
| **Live Dashboard** | GitHub Pages dashboard showing all activity in real-time |

## Architecture

```
.github/workflows/
  generate-content.yml   # Every 4 hours — generate + post
  youtube-monitor.yml    # Every 2 hours — scrape YouTube + post supporting content
  auto-reply.yml         # Every 30 min — reply to comments
  deploy-dashboard.yml   # Every hour + on push — deploy dashboard

src/
  content_engine/        # AI content generation engine
  social_posters/        # Platform-specific posting modules
  youtube_monitor/       # YouTube scraping & supporting content
  auto_reply/            # Auto-reply engine
  analytics/             # Analytics collector for dashboard
  utils/                 # Configuration and shared utilities

dashboard/               # GitHub Pages live dashboard
```

## Required GitHub Secrets

### AI Content Generation
| Secret Name | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 content generation |

### X (Twitter)
| Secret Name | Description |
|---|---|
| `X_API_KEY` | Twitter API Key (Consumer Key) |
| `X_API_SECRET` | Twitter API Secret (Consumer Secret) |
| `X_ACCESS_TOKEN` | Twitter Access Token |
| `X_ACCESS_TOKEN_SECRET` | Twitter Access Token Secret |
| `X_BEARER_TOKEN` | Twitter Bearer Token (OAuth 2.0) |

### Instagram
| Secret Name | Description |
|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | Meta Graph API long-lived access token for Instagram |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business Account ID (numeric) |

### Facebook
| Secret Name | Description |
|---|---|
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook Page long-lived access token |
| `FACEBOOK_PAGE_ID` | Facebook Page ID (numeric) |

### LinkedIn
| Secret Name | Description |
|---|---|
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn OAuth 2.0 access token |
| `LINKEDIN_PERSON_ID` | LinkedIn person URN ID (without "urn:li:person:" prefix) |

### Reddit
| Secret Name | Description |
|---|---|
| `REDDIT_CLIENT_ID` | Reddit app client ID (under script type app) |
| `REDDIT_CLIENT_SECRET` | Reddit app client secret |
| `REDDIT_USERNAME` | Reddit username |
| `REDDIT_PASSWORD` | Reddit password |

### Telegram
| Secret Name | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token from @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram chat/channel ID to post to |

### YouTube
| Secret Name | Description |
|---|---|
| `YOUTUBE_API_KEY` | Google/YouTube Data API v3 key |
| `YOUTUBE_CHANNEL_ID` | YouTube channel ID to monitor (default: @theAIsearch) |

### GitHub
| Secret Name | Description |
|---|---|
| `GH_TOKEN` | GitHub Personal Access Token (for dashboard data commits) |

## Setup

1. **Create accounts** on X, Instagram, Facebook, LinkedIn, Reddit, and Telegram
2. **Get API credentials** for each platform
3. **Add all secrets** listed above to this repository (Settings → Secrets and variables → Actions)
4. **Enable GitHub Pages** (Settings → Pages → Source: GitHub Actions)
5. **Trigger a test run** from the Actions tab using "Run workflow"

## Dashboard

The live dashboard is automatically deployed to:
`https://<your-username>.github.io/ai-content-beast/`

It shows:
- Total content generated, posts published, auto-replies sent
- Per-platform success/failure rates
- Recent content feed
- Recent YouTube supporting posts
- Recent auto-replies

## License

MIT — Use at your own risk. This agent posts aggressively.
