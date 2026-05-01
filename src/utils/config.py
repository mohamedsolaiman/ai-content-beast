"""
Central configuration for AI Content Beast.
All secret names and environment variable mappings.
"""

import os

# ─── AI Content Generation ───
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# ─── X (Twitter) ───
X_API_KEY = os.environ.get("X_API_KEY", "")
X_API_SECRET = os.environ.get("X_API_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET", "")
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")

# ─── Instagram (Meta Graph API) ───
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

# ─── Facebook (Meta Graph API) ───
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")

# ─── LinkedIn ───
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_PERSON_ID = os.environ.get("LINKEDIN_PERSON_ID", "")

# ─── Reddit ───
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD", "")

# ─── Telegram ───
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ─── YouTube ───
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "UCYMo7WFlRuKlHHoRQFYjaRw")  # @theAIsearch

# ─── GitHub (for dashboard data) ───
GH_TOKEN = os.environ.get("GH_TOKEN", "")

# ─── Content Settings ───
CONTENT_GENERATION_INTERVAL_HOURS = 4
YOUTUBE_CHECK_INTERVAL_HOURS = 2
AUTO_REPLY_DELAY_MINUTES = 15
MAX_POSTS_PER_RUN = 1
MAX_AUTO_REPLIES_PER_RUN = 5

# ─── Content Tone ───
CONTENT_TONES = [
    "aggressive thought leadership",
    "controversial hot take",
    "provocative prediction",
    "brutal honesty about AI industry",
    "bold claim with evidence",
    "disruptive insight",
]

PLATFORM_LIMITS = {
    "twitter": {"max_chars": 280, "image": True, "hashtag_limit": 5},
    "instagram": {"max_chars": 2200, "image": True, "hashtag_limit": 30},
    "facebook": {"max_chars": 63206, "image": True, "hashtag_limit": 0},
    "linkedin": {"max_chars": 3000, "image": True, "hashtag_limit": 5},
    "reddit": {"max_chars": 40000, "image": False, "hashtag_limit": 0},
    "telegram": {"max_chars": 4096, "image": True, "hashtag_limit": 0},
}
