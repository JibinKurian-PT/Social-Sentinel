"""
Comprehensive Data Science Seeder (psycopg2 sync version – no greenlet issues)
Populates PostgreSQL with 500 tweets, sentiment results, topic associations,
and 30 days of daily_aggregates for rich dashboard visualisation.
"""
import sys, os, random
from datetime import datetime, timedelta

# ── ensure src is importable ────────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import psycopg2  # type: ignore
from psycopg2.extras import execute_values  # type: ignore

# ── connection ───────────────────────────────────────────────────────────────
DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"), port=5432,
    dbname="sentiment_prod",
    user="postgres", password="postgres"
)

# ── realistic data ──────────────────────────────────────────────────────────
TOPICS = [
    {"name": "AI & Machine Learning",  "kw": ["ai","ml","llm","deep learning","neural","gpt","model","data"]},
    {"name": "Customer Support",        "kw": ["support","ticket","help","broken","fix","refund","issue","bug"]},
    {"name": "Product Pricing",         "kw": ["price","expensive","cost","subscription","plan","value","cheap"]},
    {"name": "Cloud Computing",         "kw": ["cloud","aws","azure","kubernetes","docker","deploy","server"]},
    {"name": "Cybersecurity",           "kw": ["hack","security","breach","vulnerability","threat","encrypt","firewall"]},
]

TEMPLATES = {
    "positive": [
        "The new {kw} platform is absolutely incredible! Best launch I've seen this year 🚀",
        "Just tried {kw} and wow – completely changed my workflow. Would highly recommend!",
        "Our team's productivity shot up 40% after adopting {kw}. Game changer! 💡",
        "Huge shoutout to the {kw} team – your product is flawless ⭐⭐⭐⭐⭐",
        "Finally a {kw} solution that actually works – saving me hours every day 🎉",
        "Blown away by how fast and reliable the new {kw} update is. 10/10!",
        "The {kw} demo blew my mind. Rolling this out company-wide ASAP.",
        "Seriously impressed with {kw}. The UX is clean, fast, and just works.",
        "{kw} support team resolved my issue in under 10 min. Stellar experience!",
        "Super happy with our decision to move to {kw}. Zero regrets.",
    ],
    "negative": [
        "Been waiting 3 days for {kw} support to reply. Absolutely terrible service 😡",
        "The {kw} platform keeps crashing. Switching to a competitor ASAP.",
        "Why is {kw} so expensive now?! The new pricing is outrageous.",
        "The latest {kw} update broke my entire pipeline. Unacceptable!",
        "{kw} has gone downhill fast. It used to be great, now it's a buggy mess.",
        "Submitted 5 {kw} tickets this week. Not a single response.",
        "This {kw} outage has cost us thousands. Where is the status page??",
        "Cancelled my {kw} subscription. The quality has dropped so much.",
        "The {kw} UI is confusing and unintuitive. Needs a complete redesign.",
        "{kw} charged me twice this month and I can't reach anyone. Do better.",
    ],
    "neutral": [
        "Just installed the new {kw} version. Will test it over the next few days.",
        "Reading the {kw} docs. Seems fairly comprehensive so far.",
        "Anyone here using {kw} for production workloads? Looking for feedback.",
        "The {kw} conference keynote starts in 2 hours. Curious what they'll announce.",
        "Comparing {kw} vs alternatives. Both seem to have trade-offs.",
        "Our team had a {kw} eval call today. Still deciding.",
        "New {kw} blog post is out. Covers migration steps.",
        "Attended the {kw} webinar. Informative overview of the roadmap.",
        "Setting up a {kw} demo environment. First impressions later.",
        "Reviewing the {kw} changelog for the latest release.",
    ],
}

POLARITY = {"positive": (0.25, 0.95), "negative": (-0.95, -0.25), "neutral": (-0.15, 0.15)}
CONFIDENCE = {"positive": (0.72, 0.99), "negative": (0.70, 0.99), "neutral": (0.55, 0.85)}
PLATFORMS = ["twitter", "youtube"]
LOCATIONS = [
    "New York, US", "San Francisco, US", "London, UK", "Berlin, DE",
    "Tokyo, JP", "Sydney, AU", "Toronto, CA", "Singapore, SG",
    "Mumbai, IN", "Bangalore, IN", "Paris, FR", "Amsterdam, NL",
    None, None, None,
]


def rnd(label, topic):
    kw = random.choice(topic["kw"])
    return random.choice(TEMPLATES[label]).format(kw=kw)


def main():
    print("\n🚀 Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()

    # ── create tables ────────────────────────────────────────────────────────
    print("📋 Creating tables if they don't exist...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id SERIAL PRIMARY KEY,
            platform_id VARCHAR UNIQUE,
            text TEXT NOT NULL,
            platform VARCHAR DEFAULT 'twitter',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            location VARCHAR,
            user_id VARCHAR,
            metrics JSONB
        );
        CREATE TABLE IF NOT EXISTS sentiment_results (
            id SERIAL PRIMARY KEY,
            tweet_id INTEGER REFERENCES tweets(id) ON DELETE CASCADE UNIQUE,
            label VARCHAR,
            polarity FLOAT,
            confidence FLOAT,
            model_used VARCHAR,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS topics (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE,
            keywords JSONB,
            volume INTEGER DEFAULT 0,
            avg_sentiment FLOAT DEFAULT 0.0,
            last_updated TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS topic_associations (
            id SERIAL PRIMARY KEY,
            tweet_id INTEGER REFERENCES tweets(id) ON DELETE CASCADE,
            topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
            confidence FLOAT
        );
        CREATE TABLE IF NOT EXISTS daily_aggregates (
            id SERIAL PRIMARY KEY,
            date TIMESTAMPTZ,
            platform VARCHAR,
            positive_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            neutral_count INTEGER DEFAULT 0,
            avg_polarity FLOAT DEFAULT 0.0,
            CONSTRAINT uix_date_platform UNIQUE (date, platform)
        );
    """)
    conn.commit()
    print("✅ Tables ready.")

    # ── seed topics ──────────────────────────────────────────────────────────
    print("🏷️  Seeding topics...")
    topic_ids = []
    for t in TOPICS:
        import json
        cur.execute(
            """INSERT INTO topics (name, keywords, volume, avg_sentiment)
               VALUES (%s, %s::jsonb, 0, 0.0)
               ON CONFLICT (name) DO NOTHING
               RETURNING id""",
            (t["name"], json.dumps(t["kw"]))
        )
        row = cur.fetchone()
        if row:
            topic_ids.append(row[0])
        else:
            cur.execute("SELECT id FROM topics WHERE name=%s", (t["name"],))
            topic_ids.append(cur.fetchone()[0])
    conn.commit()
    print(f"✅ {len(TOPICS)} topics ready, IDs: {topic_ids}")

    # ── seed 500 tweets + sentiment + associations ───────────────────────────
    print("🐦 Seeding 500 tweets, sentiment results and topic associations...")
    now = datetime.utcnow()
    tweet_rows, inserted_tweet_ids = [], []

    for i in range(500):
        label = random.choices(["positive", "negative", "neutral"], weights=[45, 30, 25])[0]
        tidx = random.randint(0, len(TOPICS) - 1)
        topic = TOPICS[tidx]
        platform = random.choice(PLATFORMS)
        created_at = now - timedelta(hours=random.uniform(0, 30 * 24))
        polarity = round(random.uniform(*POLARITY[label]), 4)
        confidence = round(random.uniform(*CONFIDENCE[label]), 4)
        model = random.choice(["ensemble", "bert", "textblob"])
        body = rnd(label, topic)
        pid = f"seed_{platform}_{i}_{int(created_at.timestamp())}"
        loc = random.choice(LOCATIONS)

        metrics = json.dumps({"like_count": random.randint(0, 500), "retweet_count": random.randint(0, 200)})

        cur.execute(
            """INSERT INTO tweets (platform_id, text, platform, created_at, location, user_id, metrics)
               VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
               ON CONFLICT (platform_id) DO NOTHING
               RETURNING id""",
            (pid, body, platform, created_at, loc, f"user_{random.randint(1000,9999)}", metrics)
        )
        row = cur.fetchone()
        if not row:
            continue
        tweet_id = row[0]

        cur.execute(
            """INSERT INTO sentiment_results (tweet_id, label, polarity, confidence, model_used)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (tweet_id) DO NOTHING""",
            (tweet_id, label, polarity, confidence, model)
        )

        cur.execute(
            """INSERT INTO topic_associations (tweet_id, topic_id, confidence)
               VALUES (%s, %s, %s)""",
            (tweet_id, topic_ids[tidx], round(random.uniform(0.6, 0.99), 3))
        )

    conn.commit()
    print("✅ Tweets, sentiment & associations inserted.")

    # ── seed 30 days × 2 platforms daily aggregates ──────────────────────────
    print("📅 Computing daily_aggregates for the last 30 days...")
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)

    for day_offset in range(30):
        day = base - timedelta(days=day_offset)
        for platform in PLATFORMS:
            cur.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN sr.label='positive' THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN sr.label='negative' THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN sr.label='neutral'  THEN 1 ELSE 0 END), 0),
                    COALESCE(AVG(sr.polarity), 0.0)
                FROM tweets t
                JOIN sentiment_results sr ON sr.tweet_id = t.id
                WHERE t.platform = %s AND DATE(t.created_at) = DATE(%s)
            """, (platform, day))

            pos, neg, neu, avg_pol = cur.fetchone()

            # Fallback: synthesize if no real data for this day/platform
            if pos + neg + neu == 0:
                pos = random.randint(15, 60)
                neg = random.randint(8, 35)
                neu = random.randint(10, 40)
                avg_pol = round(random.uniform(-0.2, 0.5), 4)

            cur.execute("""
                INSERT INTO daily_aggregates (date, platform, positive_count, negative_count, neutral_count, avg_polarity)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, platform) DO UPDATE
                    SET positive_count = EXCLUDED.positive_count,
                        negative_count = EXCLUDED.negative_count,
                        neutral_count  = EXCLUDED.neutral_count,
                        avg_polarity   = EXCLUDED.avg_polarity
            """, (day, platform, int(pos), int(neg), int(neu), float(avg_pol)))

    conn.commit()
    print("✅ 30 days × 2 platforms of daily_aggregates seeded.")

    # ── update topic volume stats ─────────────────────────────────────────────
    print("📊 Updating topic volumes...")
    cur.execute("""
        UPDATE topics t SET
            volume       = sub.vol,
            avg_sentiment= sub.avg_pol,
            last_updated = NOW()
        FROM (
            SELECT ta.topic_id, COUNT(*) AS vol, AVG(sr.polarity) AS avg_pol
            FROM topic_associations ta
            JOIN sentiment_results sr ON sr.tweet_id = ta.tweet_id
            GROUP BY ta.topic_id
        ) sub
        WHERE t.id = sub.topic_id
    """)
    conn.commit()
    print("✅ Topic volumes updated.")

    cur.close()
    conn.close()

    print("\n🎉 Seed complete! Summary:")
    print("   • 500 tweets  →  tweets table")
    print("   • 500 sentiment results (label, polarity, confidence, model)")
    print("   • 500 topic associations")
    print("   • 60 daily_aggregate rows (30 days × twitter + youtube)")
    print("   • 5 topics with volume + avg_sentiment computed")
    print("\n👉 Refresh http://localhost:8501 to see your analytics!")


if __name__ == "__main__":
    main()
