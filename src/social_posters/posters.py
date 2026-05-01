"""Social media posters — one module per platform. Each reads latest content and posts."""

import json
import os
import urllib.request
import urllib.error


# ─── Twitter / X Poster ───
class TwitterPoster:
    """Posts content to X using API v2."""

    def __init__(self):
        self.bearer_token = os.environ.get("X_BEARER_TOKEN", "")
        self.api_key = os.environ.get("X_API_KEY", "")
        self.api_secret = os.environ.get("X_API_SECRET", "")
        self.access_token = os.environ.get("X_ACCESS_TOKEN", "")
        self.access_secret = os.environ.get("X_ACCESS_TOKEN_SECRET", "")
        if not self.bearer_token:
            raise ValueError("X_BEARER_TOKEN is required")

    def post(self, text: str) -> dict:
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
        body = json.dumps({"text": text}).encode()

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                print(f"Tweet posted: {result.get('data', {}).get('id')}")
                return {"success": True, "platform": "twitter", "response": result}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"Twitter error {e.code}: {error_body}")
            return {"success": False, "platform": "twitter", "error": error_body}


# ─── Instagram Poster ───
class InstagramPoster:
    """Posts content to Instagram using Meta Graph API."""

    def __init__(self):
        self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
        self.account_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
        if not self.access_token or not self.account_id:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID required")

    def post(self, text: str) -> dict:
        url = f"https://graph.facebook.com/v19.0/{self.account_id}/media"
        params = urllib.parse.urlencode({
            "message": text[:2200],
            "access_token": self.access_token,
        })

        # Create container
        req = urllib.request.Request(f"{url}?{params}", method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                container_id = result.get("id")
                if not container_id:
                    return {"success": False, "platform": "instagram", "error": "No container ID returned"}

                # Publish container
                pub_url = f"https://graph.facebook.com/v19.0/{container_id}/publish"
                pub_params = urllib.parse.urlencode({"access_token": self.access_token})
                pub_req = urllib.request.Request(f"{pub_url}?{pub_params}", method="POST")
                with urllib.request.urlopen(pub_req, timeout=30) as pub_resp:
                    pub_result = json.loads(pub_resp.read().decode())
                    print(f"Instagram post published: {pub_result.get('id')}")
                    return {"success": True, "platform": "instagram", "response": pub_result}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"Instagram error {e.code}: {error_body}")
            return {"success": False, "platform": "instagram", "error": error_body}


# ─── Facebook Poster ───
class FacebookPoster:
    """Posts content to a Facebook Page using Meta Graph API."""

    def __init__(self):
        self.page_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        self.page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
        if not self.page_token or not self.page_id:
            raise ValueError("FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID required")

    def post(self, text: str) -> dict:
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
        params = urllib.parse.urlencode({
            "message": text,
            "access_token": self.page_token,
        })

        req = urllib.request.Request(f"{url}?{params}", method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                print(f"Facebook post published: {result.get('id')}")
                return {"success": True, "platform": "facebook", "response": result}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"Facebook error {e.code}: {error_body}")
            return {"success": False, "platform": "facebook", "error": error_body}


# ─── LinkedIn Poster ───
class LinkedInPoster:
    """Posts content to LinkedIn using LinkedIn API v2."""

    def __init__(self):
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
        self.person_id = os.environ.get("LINKEDIN_PERSON_ID", "")
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN is required")

    def post(self, text: str) -> dict:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        author = f"urn:li:person:{self.person_id}" if self.person_id else ""
        body = json.dumps({
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text[:3000]},
                    "shareMediaCategory": "ARTICLE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }).encode()

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                print(f"LinkedIn post published: {result}")
                return {"success": True, "platform": "linkedin", "response": result}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"LinkedIn error {e.code}: {error_body}")
            return {"success": False, "platform": "linkedin", "error": error_body}


# ─── Reddit Poster ───
class RedditPoster:
    """Posts content to Reddit using API."""

    def __init__(self):
        self.client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self.client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        self.username = os.environ.get("REDDIT_USERNAME", "")
        self.password = os.environ.get("REDDIT_PASSWORD", "")
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            raise ValueError("REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD required")

    def _get_auth_token(self) -> str:
        url = "https://www.reddit.com/api/v1/access_token"
        credentials = f"{self.client_id}:{self.client_secret}".encode()
        headers = {
            "Authorization": f"Basic {__import__('base64').b64encode(credentials).decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = f"grant_type=password&username={self.username}&password={self.password}".encode()
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())["access_token"]

    def post(self, text: str, subreddit: str = "artificial") -> dict:
        token = self._get_auth_token()
        url = f"https://oauth.reddit.com/api/submit"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "AIContentBeast/1.0",
        }
        # Split text into title and body
        lines = text.split("\n")
        title = lines[0][:300]
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""

        params = urllib.parse.urlencode({
            "sr": subreddit,
            "title": title,
            "kind": "self" if body else "link",
            "text": body,
            "resubmit": "true",
        })
        req = urllib.request.Request(url, data=params.encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                print(f"Reddit post submitted to r/{subreddit}")
                return {"success": True, "platform": "reddit", "subreddit": subreddit, "response": result}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"Reddit error {e.code}: {error_body}")
            return {"success": False, "platform": "reddit", "error": error_body}


# ─── Telegram Poster ───
class TelegramPoster:
    """Posts content to Telegram using Bot API."""

    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required")

    def post(self, text: str) -> dict:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = urllib.parse.urlencode({
            "chat_id": self.chat_id,
            "text": text[:4096],
            "parse_mode": "HTML",
        })

        req = urllib.request.Request(f"{url}?{params}", method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                print(f"Telegram message sent: {result.get('result', {}).get('message_id')}")
                return {"success": True, "platform": "telegram", "response": result}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"Telegram error {e.code}: {error_body}")
            return {"success": False, "platform": "telegram", "error": error_body}


# ─── Master Poster — orchestrates all platforms ───
class MasterPoster:
    """Posts content to all configured platforms."""

    def __init__(self):
        self.posters = {
            "twitter": TwitterPoster,
            "instagram": InstagramPoster,
            "facebook": FacebookPoster,
            "linkedin": LinkedInPoster,
            "reddit": RedditPoster,
            "telegram": TelegramPoster,
        }

    def post_to_all(self, platform_versions: dict) -> dict:
        results = {}
        for platform, poster_class in self.posters.items():
            content = platform_versions.get(platform, "")
            if not content:
                print(f"No content for {platform}, skipping")
                continue
            try:
                poster = poster_class()
                results[platform] = poster.post(content)
            except ValueError as e:
                results[platform] = {"success": False, "platform": platform, "error": str(e)}
                print(f"Skipping {platform}: {e}")
            except Exception as e:
                results[platform] = {"success": False, "platform": platform, "error": str(e)}

        return results


def main():
    content_file = "data/latest_content.json"
    if not os.path.exists(content_file):
        print("No content to post. Run content engine first.")
        return

    with open(content_file, "r") as f:
        content = json.load(f)

    poster = MasterPoster()
    results = poster.post_to_all(content.get("platform_versions", {}))

    # Save results
    results_file = f"data/analytics/post_results_{os.path.basename(content_file)}"
    os.makedirs("data/analytics", exist_ok=True)
    with open(results_file, "w") as f:
        json.dump({
            "content_id": content.get("content_id"),
            "timestamp": content.get("timestamp"),
            "results": results,
        }, f, indent=2)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
