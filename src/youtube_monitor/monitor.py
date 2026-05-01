"""YouTube Monitor — Scrapes @theAIsearch channel for new videos and generates supporting content."""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

from utils.config import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID


class YouTubeMonitor:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is required")

    def _fetch_latest_videos(self, max_results: int = 5) -> list:
        """Fetch the latest videos from @theAIsearch channel."""
        # Get the channel's uploads playlist ID
        playlist_url = (
            f"https://www.googleapis.com/youtube/v3/channels?"
            f"part=contentDetails&id={YOUTUBE_CHANNEL_ID}&key={self.api_key}"
        )

        try:
            req = urllib.request.Request(playlist_url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except Exception as e:
            print(f"Error fetching playlist ID: {e}")
            return []

        # Fetch videos from uploads playlist
        videos_url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems?"
            f"part=snippet,status&playlistId={playlist_id}&maxResults={max_results}"
            f"&key={self.api_key}"
        )

        try:
            req = urllib.request.Request(videos_url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return []

        videos = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            video_id = snippet.get("resourceId", {}).get("videoId", "")
            if not video_id:
                continue
            videos.append({
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:500],
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })

        return videos

    def check_for_new_videos(self, cache_file: str = "data/youtube_cache/processed.json") -> list:
        """Check for new videos since last check. Returns list of new videos."""
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)

        # Load cache of already-processed video IDs
        processed = set()
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                processed = set(json.load(f))

        # Fetch latest videos
        latest_videos = self._fetch_latest_videos(10)

        # Filter to only new ones
        new_videos = [v for v in latest_videos if v["video_id"] not in processed]

        if new_videos:
            # Update cache
            new_ids = processed | {v["video_id"] for v in new_videos}
            with open(cache_file, "w") as f:
                json.dump(list(new_ids), f)
            print(f"Found {len(new_videos)} new video(s) from @theAIsearch")
        else:
            print("No new videos from @theAIsearch")

        return new_videos

    def generate_supporting_content(self, video: dict) -> str:
        """Generate a supporting tweet/post about a YouTube video using OpenAI."""
        from content_engine.engine import ContentEngine

        engine = ContentEngine()
        prompt = f"""You are an AI marketing agent. Write a SHORT, punchy supporting post about this new YouTube video.

VIDEO TITLE: {video['title']}
VIDEO URL: {video['url']}
VIDEO DESCRIPTION: {video['description']}

RULES:
- Keep it under 280 characters for Twitter (you'll output ONE version)
- Hook the reader — make them want to watch
- Tag the creator reference: @theAIsearch
- Include the video URL
- Be provocative but supportive
- ONE hot takeaway from the title/description
- Output ONLY the post text, nothing else"""

        return engine._call_openai(prompt)

    def save_youtube_content(self, video: dict, content: str, output_dir: str = "data/content_log"):
        """Save YouTube-derived content to log."""
        os.makedirs(output_dir, exist_ok=True)
        entry = {
            "type": "youtube_supporting",
            "video_id": video["video_id"],
            "video_title": video["title"],
            "video_url": video["url"],
            "generated_content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "generated",
        }
        filename = f"yt_{video['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            json.dump(entry, f, indent=2)
        return filepath


def main():
    monitor = YouTubeMonitor()
    new_videos = monitor.check_for_new_videos()

    results = []
    for video in new_videos:
        content = monitor.generate_supporting_content(video)
        saved = monitor.save_youtube_content(video, content)
        results.append({
            "video_id": video["video_id"],
            "title": video["title"],
            "content": content,
            "saved_to": saved,
        })

    if results:
        with open("data/latest_youtube_content.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"Generated content for {len(results)} video(s)")
    else:
        print("No new content generated")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
