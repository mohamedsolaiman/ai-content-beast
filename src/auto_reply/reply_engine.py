"""Auto-Reply Engine — Monitors comments and replies to some to boost engagement."""

import json
import os
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone


class AutoReplyEngine:
    """Checks for comments/replies on posts and generates AI-powered replies."""

    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY", "")
        self.replied_cache_file = "data/analytics/replied_comments.json"
        os.makedirs("data/analytics", exist_ok=True)

    def _load_replied_cache(self) -> set:
        if os.path.exists(self.replied_cache_file):
            with open(self.replied_cache_file, "r") as f:
                return set(json.load(f))
        return set()

    def _save_replied_cache(self, cache: set):
        with open(self.replied_cache_file, "w") as f:
            json.dump(list(cache), f)

    def _generate_reply(self, comment_text: str, platform: str) -> str:
        """Generate a contextual reply using OpenAI."""
        if not self.openai_key:
            return random.choice([
                "Great point! The AI landscape is shifting faster than most realize.",
                "Spot on. This is exactly the kind of thinking that separates signal from noise.",
                "Agreed — and the implications are bigger than most people understand.",
                "This perspective is underrated. Most miss the second-order effects.",
                "Exactly. The real question is what happens when this scales 10x.",
            ])

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        prompt = f"""You are an aggressive AI thought leader. Reply to this comment on {platform.upper()}.

COMMENT: {comment_text}

RULES:
- Be confident and authoritative
- Keep reply under 100 words
- Either agree emphatically with added insight OR respectfully disagree with evidence
- Ask a follow-up question to keep the conversation going
- No emojis
- Output ONLY the reply text"""

        body = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.8,
        }).encode()

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"].strip()

    # ─── Platform-specific comment fetching and replying ───

    def reply_on_twitter(self):
        """Fetch recent mentions and reply to some."""
        bearer_token = os.environ.get("X_BEARER_TOKEN", "")
        if not bearer_token:
            return []

        replied = self._load_replied_cache()
        replies_made = []

        # Get recent mentions
        url = "https://api.twitter.com/2/users/me/mentions?max_results=20&tweet.fields=conversation_id,in_reply_to_user_id"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Twitter mentions error: {e}")
            return replies_made

        mentions = data.get("data", [])
        # Reply to max 5
        for mention in mentions[:5]:
            comment_id = mention["id"]
            if comment_id in replied:
                continue

            reply_text = self._generate_reply(mention.get("text", ""), "twitter")

            # Post reply
            reply_url = "https://api.twitter.com/2/tweets"
            reply_headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
            }
            reply_body = json.dumps({
                "text": reply_text,
                "reply": {"in_reply_to_tweet_id": comment_id},
            }).encode()
            reply_req = urllib.request.Request(
                reply_url, data=reply_body, headers=reply_headers, method="POST"
            )

            try:
                with urllib.request.urlopen(reply_req, timeout=30) as reply_resp:
                    result = json.loads(reply_resp.read().decode())
                    replied.add(comment_id)
                    replies_made.append({
                        "platform": "twitter",
                        "comment_id": comment_id,
                        "reply": reply_text,
                        "status": "success",
                    })
            except Exception as e:
                print(f"Reply error: {e}")

        self._save_replied_cache(replied)
        return replies_made

    def reply_on_reddit(self):
        """Fetch recent comments on Reddit posts and reply to some."""
        client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        username = os.environ.get("REDDIT_USERNAME", "")
        password = os.environ.get("REDDIT_PASSWORD", "")

        if not all([client_id, client_secret, username, password]):
            return []

        import base64

        replied = self._load_replied_cache()
        replies_made = []

        # Auth
        url = "https://www.reddit.com/api/v1/access_token"
        creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = f"grant_type=password&username={username}&password={password}".encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                token = json.loads(resp.read().decode())["access_token"]
        except Exception as e:
            print(f"Reddit auth error: {e}")
            return replies_made

        # Get user's recent posts comments
        comments_url = "https://oauth.reddit.com/user/me/comments?limit=20"
        com_headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "AIContentBeast/1.0",
        }
        com_req = urllib.request.Request(comments_url, headers=com_headers)

        try:
            with urllib.request.urlopen(com_req, timeout=30) as resp:
                comments_data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Reddit comments error: {e}")
            return replies_made

        for child in comments_data.get("data", {}).get("children", [])[:5]:
            comment = child["data"]
            comment_id = comment["id"]

            if f"reddit_{comment_id}" in replied:
                continue

            body_text = comment.get("body", "")
            reply_text = self._generate_reply(body_text, "reddit")

            # Post reply
            reply_url = "https://oauth.reddit.com/api/comment"
            reply_params = urllib.parse.urlencode({
                "thing_id": f"t1_{comment_id}",
                "text": reply_text,
            })
            reply_req = urllib.request.Request(
                reply_url,
                data=reply_params.encode(),
                headers={**com_headers, "Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )

            try:
                with urllib.request.urlopen(reply_req, timeout=30) as reply_resp:
                    if reply_resp.status == 200:
                        replied.add(f"reddit_{comment_id}")
                        replies_made.append({
                            "platform": "reddit",
                            "comment_id": comment_id,
                            "reply": reply_text,
                            "status": "success",
                        })
            except Exception as e:
                print(f"Reddit reply error: {e}")

        self._save_replied_cache(replied)
        return replies_made

    def reply_on_telegram(self):
        """Fetch recent messages in Telegram chat and reply to some."""
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not bot_token or not chat_id:
            return []

        replied = self._load_replied_cache()
        replies_made = []

        # Get updates
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Telegram updates error: {e}")
            return replies_made

        for update in data.get("result", [])[-10:]:
            message = update.get("message", {})
            msg_id = message.get("message_id")
            text = message.get("text", "")
            from_user = message.get("from", {}).get("is_bot", False)

            if not text or not msg_id or from_user:
                continue

            if f"tg_{msg_id}" in replied:
                continue

            # Only reply to ~30% of messages for natural feel
            if random.random() > 0.3:
                continue

            reply_text = self._generate_reply(text, "telegram")

            send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            params = urllib.parse.urlencode({
                "chat_id": chat_id,
                "text": reply_text,
                "reply_to_message_id": msg_id,
            })
            send_req = urllib.request.Request(f"{send_url}?{params}", method="POST")

            try:
                with urllib.request.urlopen(send_req, timeout=30) as send_resp:
                    if send_resp.status == 200:
                        replied.add(f"tg_{msg_id}")
                        replies_made.append({
                            "platform": "telegram",
                            "message_id": msg_id,
                            "reply": reply_text,
                            "status": "success",
                        })
            except Exception as e:
                print(f"Telegram reply error: {e}")

        self._save_replied_cache(replied)
        return replies_made

    def run_all(self):
        """Run auto-reply on all available platforms."""
        all_replies = []
        print("Running auto-reply on Twitter...")
        all_replies.extend(self.reply_on_twitter())
        print("Running auto-reply on Reddit...")
        all_replies.extend(self.reply_on_reddit())
        print("Running auto-reply on Telegram...")
        all_replies.extend(self.reply_on_telegram())

        # Save summary
        summary_file = f"data/analytics/auto_reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w") as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_replies": len(all_replies),
                "replies": all_replies,
            }, f, indent=2)

        print(f"Auto-reply complete: {len(all_replies)} replies sent")
        return all_replies


def main():
    engine = AutoReplyEngine()
    results = engine.run_all()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
