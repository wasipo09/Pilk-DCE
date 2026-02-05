#!/usr/bin/env python3
"""
Crypto News RSS Scraper
Pulls headlines from crypto news feeds and scores sentiment.
"""

import feedparser
from datetime import datetime
import re

# RSS Feeds
RSS_FEEDS = [
    ("CoinDesk", "https://feeds.coindesk.com/coindesk/news"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
    ("Bitcoin Magazine", "https://www.bitcoinmagazine.com/feed.xml"),
    ("Decrypt", "https://decrypt.co/feed"),
    ("The Block", "https://www.theblock.co/rss.xml"),
]

# Sentiment keywords
BULLISH = ["bullish", "surge", "rally", "pump", "soar", "gain", "positive", "bull", "up",
            "higher", "record", "peak", "boost", "rally", "momentum", "strong", "growth",
            "adoption", "breakthrough", "breakout", "bounce", "recovery", "uptrend"]

BEARISH = ["bearish", "crash", "dump", "plunge", "drop", "fall", "negative", "bear", "down",
            "lower", "fear", "panic", "sell", "dump", "correction", "decline", "weak",
            "concern", "warning", "risk", "downtrend", "collapse", "sell-off", "pressure"]


def score_sentiment(text):
    """Simple keyword-based sentiment scoring."""
    text_lower = text.lower()
    bullish_count = sum(1 for word in BULLISH if word in text_lower)
    bearish_count = sum(1 for word in BEARISH if word in text_lower)

    if bullish_count > bearish_count:
        return "bullish", bullish_count - bearish_count
    elif bearish_count > bullish_count:
        return "bearish", bearish_count - bullish_count
    return "neutral", 0


def fetch_news(max_per_feed=5):
    """Fetch and parse news from RSS feeds."""
    headlines = []

    for source, url in RSS_FEEDS:
        try:
            print(f"Fetching {source}...")
            feed = feedparser.parse(url)

            for entry in feed.entries[:max_per_feed]:
                title = entry.title
                url_link = entry.link
                published = entry.get("published", "Unknown")

                # Score sentiment
                sentiment, score = score_sentiment(title + " " + entry.get("summary", ""))

                headlines.append({
                    "source": source,
                    "title": title,
                    "url": url_link,
                    "published": published,
                    "sentiment": sentiment,
                    "score": score
                })

        except Exception as e:
            print(f"Error fetching {source}: {e}")

    return headlines


def summarize_news(headlines):
    """Generate a summary of the news."""
    if not headlines:
        return "No news fetched."

    # Count sentiments
    bullish = sum(1 for h in headlines if h["sentiment"] == "bullish")
    bearish = sum(1 for h in headlines if h["sentiment"] == "bearish")
    neutral = sum(1 for h in headlines if h["sentiment"] == "neutral")

    # Top picks by score
    top_bullish = sorted([h for h in headlines if h["sentiment"] == "bullish"], key=lambda x: x["score"], reverse=True)[:3]
    top_bearish = sorted([h for h in headlines if h["sentiment"] == "bearish"], key=lambda x: x["score"], reverse=True)[:3]

    return {
        "totals": {"bullish": bullish, "bearish": bearish, "neutral": neutral},
        "top_bullish": top_bullish,
        "top_bearish": top_bearish,
        "all": headlines
    }


def main():
    print("=" * 50)
    print("Crypto News Scraper")
    print("=" * 50)
    print()

    headlines = fetch_news(max_per_feed=5)
    summary = summarize_news(headlines)

    # Print summary
    print("\n📊 SENTIMENT SUMMARY")
    print("-" * 50)
    totals = summary["totals"]
    total = totals["bullish"] + totals["bearish"] + totals["neutral"]
    print(f"Total headlines: {total}")
    print(f"Bullish: {totals['bullish']} | Bearish: {totals['bearish']} | Neutral: {totals['neutral']}")

    # Overall bias
    if totals["bullish"] > totals["bearish"]:
        print(f"🟢 Overall: BULLISH (+{totals['bullish'] - totals['bearish']})")
    elif totals["bearish"] > totals["bullish"]:
        print(f"🔴 Overall: BEARISH (+{totals['bearish'] - totals['bullish']})")
    else:
        print("⚪ Overall: NEUTRAL")

    print()

    # Top bullish headlines
    if summary["top_bullish"]:
        print("🟢 TOP BULLISH HEADLINES")
        print("-" * 50)
        for i, h in enumerate(summary["top_bullish"], 1):
            print(f"{i}. [{h['source']}] {h['title']}")
            print(f"   Score: +{h['score']} | {h['url']}")
            print()

    # Top bearish headlines
    if summary["top_bearish"]:
        print("🔴 TOP BEARISH HEADLINES")
        print("-" * 50)
        for i, h in enumerate(summary["top_bearish"], 1):
            print(f"{i}. [{h['source']}] {h['title']}")
            print(f"   Score: +{h['score']} | {h['url']}")
            print()

    # Save to file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file = "/Users/pilk/.openclaw/workspace/crypto_news_report.txt"

    with open(output_file, "w") as f:
        f.write(f"CRYPTO NEWS REPORT - {timestamp}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total headlines: {total}\n")
        f.write(f"Bullish: {totals['bullish']} | Bearish: {totals['bearish']} | Neutral: {totals['neutral']}\n\n")

        f.write("TOP BULLISH:\n")
        for h in summary["top_bullish"]:
            f.write(f"- [{h['source']}] {h['title']}\n")
            f.write(f"  Score: +{h['score']}\n\n")

        f.write("TOP BEARISH:\n")
        for h in summary["top_bearish"]:
            f.write(f"- [{h['source']}] {h['title']}\n")
            f.write(f"  Score: +{h['score']}\n\n")

        f.write("\nALL HEADLINES:\n")
        for h in headlines:
            f.write(f"[{h['source']}] {h['title']}\n")
            f.write(f"Sentiment: {h['sentiment']} | {h['url']}\n\n")

    print(f"\n✅ Report saved to: {output_file}")


if __name__ == "__main__":
    main()
