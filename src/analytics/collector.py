"""Analytics collector — Aggregates all activity data for the dashboard."""

import json
import os
import glob
from datetime import datetime, timezone


def collect_analytics(base_dir: str = ".") -> dict:
    """Collect all analytics data and produce a summary for the dashboard."""
    analytics = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_content_generated": 0,
        "total_posts_published": 0,
        "total_auto_replies": 0,
        "total_youtube_content": 0,
        "platform_stats": {
            "twitter": {"posted": 0, "failed": 0},
            "instagram": {"posted": 0, "failed": 0},
            "facebook": {"posted": 0, "failed": 0},
            "linkedin": {"posted": 0, "failed": 0},
            "reddit": {"posted": 0, "failed": 0},
            "telegram": {"posted": 0, "failed": 0},
        },
        "recent_content": [],
        "recent_youtube": [],
        "recent_replies": [],
    }

    # Count generated content
    content_logs = glob.glob("data/content_log/*.json")
    analytics["total_content_generated"] = len(content_logs)

    # Get most recent content items
    content_logs.sort(key=os.path.getmtime, reverse=True)
    for log_file in content_logs[:5]:
        try:
            with open(log_file, "r") as f:
                item = json.load(f)
            analytics["recent_content"].append({
                "content_id": item.get("content_id", ""),
                "topic": item.get("topic", ""),
                "tone": item.get("tone", ""),
                "timestamp": item.get("timestamp", ""),
                "type": item.get("type", "main"),
            })
        except Exception:
            pass

    # Count YouTube content
    yt_logs = glob.glob("data/content_log/yt_*.json")
    analytics["total_youtube_content"] = len(yt_logs)
    for log_file in yt_logs[:5]:
        try:
            with open(log_file, "r") as f:
                item = json.load(f)
            analytics["recent_youtube"].append({
                "video_title": item.get("video_title", ""),
                "video_url": item.get("video_url", ""),
                "timestamp": item.get("timestamp", ""),
            })
        except Exception:
            pass

    # Analyze post results
    result_files = glob.glob("data/analytics/post_results_*.json")
    for rf in result_files:
        try:
            with open(rf, "r") as f:
                data = json.load(f)
            for platform, result in data.get("results", {}).items():
                analytics["platform_stats"][platform][
                    "posted" if result.get("success") else "failed"
                ] += 1
                analytics["total_posts_published"] += result.get("success", 0)
        except Exception:
            pass

    # Analyze auto-replies
    reply_files = glob.glob("data/analytics/auto_reply_*.json")
    for rf in reply_files:
        try:
            with open(rf, "r") as f:
                data = json.load(f)
            analytics["total_auto_replies"] += data.get("total_replies", 0)
            for reply in data.get("replies", [])[:3]:
                analytics["recent_replies"].append({
                    "platform": reply.get("platform", ""),
                    "reply": reply.get("reply", "")[:100],
                })
        except Exception:
            pass

    # Trim recent replies to last 10
    analytics["recent_replies"] = analytics["recent_replies"][-10:]

    return analytics


def save_analytics_for_dashboard(analytics: dict, output_file: str = "dashboard/data.json"):
    """Save analytics to dashboard data file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(analytics, f, indent=2)
    print(f"Dashboard data saved: {output_file}")


def main():
    analytics = collect_analytics()
    save_analytics_for_dashboard(analytics)
    print(json.dumps(analytics, indent=2))


if __name__ == "__main__":
    main()
