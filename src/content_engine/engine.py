"""
AI Content Engine — Generates original, aggressive AI marketing content
using OpenAI GPT-4. Produces platform-optimized versions for all 6 platforms.
"""

import json
import os
import random
import hashlib
from datetime import datetime, timezone

from utils.config import (
    CONTENT_TONES,
    PLATFORM_LIMITS,
    OPENAI_API_KEY,
    CONTENT_GENERATION_INTERVAL_HOURS,
)


class ContentEngine:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    def _pick_tone(self) -> str:
        return random.choice(CONTENT_TONES)

    def _generate_topic(self) -> str:
        topics = [
            "Why 90% of AI startups will die by 2027",
            "The real reason GPT-class models are overrated for enterprise",
            "AGI is a distraction — here's what actually matters",
            "Why AI researchers are ignoring the biggest threat",
            "The hidden monopoly no one talks about in AI infrastructure",
            "Why your company's AI strategy is already obsolete",
            "The dirty secret about AI code assistants",
            "Why open source AI will destroy Big Tech's moat",
            "The coming AI regulation bloodbath",
            "Why AI safety is mostly theater",
            "The real cost of training frontier AI models — you won't believe it",
            "Why AI agents will replace 80% of SaaS products",
            "The uncomfortable truth about AI bias",
            "Why the AI talent bubble is about to burst",
            "How AI is quietly reshaping geopolitical power",
            "Why most AI ethics boards are completely useless",
            "The real reason companies can't ship AI products",
            "Why AI-powered search is Google's existential crisis",
            "The AI chip shortage nobody is talking about",
            "Why synthetic data is both the cure and the poison",
        ]
        return random.choice(topics)

    def _build_prompt(self, topic: str, tone: str, platform: str = "general") -> str:
        limits = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["twitter"])
        max_chars = limits["max_chars"]
        hashtag_note = ""
        if limits["hashtag_limit"] > 0:
            hashtag_note = f"Include up to {limits['hashtag_limit']} relevant hashtags."

        return f"""You are an aggressive, bold AI thought leader who creates viral marketing content. Your tone is {tone}.

TOPIC: {topic}

RULES:
- Be provocative but credible — back claims with logic
- Use strong, confident language
- Include a hook in the first line
- End with a call to action or thought-provoking question
- Maximum {max_chars} characters
- {hashtag_note}
- NO markdown formatting unless the platform supports it
- Do NOT use emojis unless it's Instagram or Telegram
- Make it shareable — people should want to retweet/repost this

PLATFORM: {platform.upper()}

Generate ONLY the content text. No explanations, no preamble. Just the post."""

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API to generate content."""
        try:
            import urllib.request
            import urllib.error

            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            body = json.dumps({
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an elite AI marketing strategist who creates viral, aggressive, thought-provoking content about artificial intelligence. Your content generates massive engagement through bold claims and sharp insights.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 1000,
                "temperature": 0.9,
            }).encode()

            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise

    def generate_content(self) -> dict:
        """Generate a full content set: topic, general version, and platform-optimized versions."""
        topic = self._generate_topic()
        tone = self._pick_tone()
        timestamp = datetime.now(timezone.utc).isoformat()

        content_id = hashlib.sha256(f"{topic}{timestamp}".encode()).hexdigest()[:12]

        # Generate general/base content first
        base_prompt = self._build_prompt(topic, tone, "general")
        base_content = self._call_openai(base_prompt)

        # Generate platform-optimized versions
        platform_versions = {}
        for platform in ["twitter", "instagram", "facebook", "linkedin", "reddit", "telegram"]:
            plat_prompt = self._build_prompt(topic, tone, platform)
            platform_versions[platform] = self._call_openai(plat_prompt)

        result = {
            "content_id": content_id,
            "timestamp": timestamp,
            "topic": topic,
            "tone": tone,
            "base_content": base_content,
            "platform_versions": platform_versions,
            "status": "generated",
            "posted_to": [],
        }

        return result

    def save_content(self, content: dict, log_dir: str = "data/content_log"):
        """Save generated content to JSON log file."""
        os.makedirs(log_dir, exist_ok=True)
        filename = f"{content['content_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(log_dir, filename)
        with open(filepath, "w") as f:
            json.dump(content, f, indent=2)
        print(f"Content saved: {filepath}")
        return filepath


def main():
    engine = ContentEngine()
    content = engine.generate_content()
    saved = engine.save_content(content)

    # Output the result for the GitHub Actions workflow to capture
    output = {
        "content_id": content["content_id"],
        "timestamp": content["timestamp"],
        "topic": content["topic"],
        "tone": content["tone"],
        "platform_versions": content["platform_versions"],
        "saved_to": saved,
    }

    # Save to a known location for the workflow
    with open("data/latest_content.json", "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
