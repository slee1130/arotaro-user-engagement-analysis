"""
Arotaro User Engagement Analysis
Python/Pandas analysis that mirrors the dbt mart layer
"""
import pandas as pd
import json

# ── Load seed data ────────────────────────────────────────────────────────────
sessions = pd.read_csv("seeds/conversation_sessions.csv", parse_dates=["created_at", "updated_at"])
messages = pd.read_csv("seeds/conversation_messages.csv", parse_dates=["created_at"])
users    = pd.read_csv("seeds/concerned_users.csv",       parse_dates=["created_at"])
devices  = pd.read_csv("seeds/user_devices.csv",          parse_dates=["last_seen_at", "created_at"])

print(f"Loaded: {len(users)} users | {len(sessions)} sessions | {len(messages)} messages")

# ── 1. Session metrics ────────────────────────────────────────────────────────
sessions["session_duration_minutes"] = sessions["timer_duration"] / 60

msg_agg = (
    messages.groupby("conversation_session_id")
    .agg(
        total_messages=("id", "count"),
        human_messages=("conversant", lambda x: (x == "HUMAN").sum()),
        satisfaction_score=("satisfaction_score", "max"),
    )
    .reset_index()
    .rename(columns={"conversation_session_id": "id"})
)

session_metrics = sessions.merge(msg_agg, on="id", how="left")

# ── 2. Topic-level engagement ─────────────────────────────────────────────────
topic_summary = (
    session_metrics.groupby("topic")
    .agg(
        total_sessions=("id", "count"),
        avg_duration_min=("session_duration_minutes", "mean"),
        avg_messages=("total_messages", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        dropoff_rate=("is_dropoff", "mean"),
    )
    .round(2)
    .sort_values("avg_duration_min", ascending=False)
    .reset_index()
)
topic_summary["dropoff_rate_pct"] = (topic_summary["dropoff_rate"] * 100).round(1)

print("\n── Topic Engagement Summary ──────────────────────────────────")
print(topic_summary[["topic","total_sessions","avg_duration_min","avg_messages","avg_satisfaction","dropoff_rate_pct"]].to_string(index=False))

# ── 3. User retention ─────────────────────────────────────────────────────────
user_session_agg = (
    session_metrics.groupby("concerned_user_id")
    .agg(
        total_sessions=("id", "count"),
        completed_sessions=("is_dropoff", lambda x: (~x).sum()),
        avg_duration=("session_duration_minutes", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        first_session=("created_at", "min"),
        last_session=("created_at", "max"),
    )
    .reset_index()
    .rename(columns={"concerned_user_id": "id"})
)

user_session_agg["user_type"] = user_session_agg["total_sessions"].apply(
    lambda x: "returning" if x >= 3 else "new"
)
user_session_agg["completion_rate"] = (
    user_session_agg["completed_sessions"] / user_session_agg["total_sessions"] * 100
).round(1)

user_data = users.merge(devices[["user_id","platform","locale","timezone","last_seen_at"]], left_on="id", right_on="user_id", how="left")
user_retention = user_data.merge(user_session_agg, on="id", how="left")

# ── 4. Key metrics summary ────────────────────────────────────────────────────
print("\n── Key Metrics ──────────────────────────────────────────────")
print(f"  Total users:          {len(users):,}")
print(f"  Total sessions:       {len(sessions):,}")
print(f"  Total messages:       {len(messages):,}")
print(f"  Avg session duration: {sessions['session_duration_minutes'].mean():.1f} min")
print(f"  Overall drop-off rate:{sessions['is_dropoff'].mean()*100:.1f}%")
print(f"  Returning users:      {(user_session_agg['user_type']=='returning').sum():,} ({(user_session_agg['user_type']=='returning').mean()*100:.1f}%)")

print("\n── Returning vs New Users ───────────────────────────────────")
user_type_summary = (
    user_retention.groupby("user_type")
    .agg(
        count=("id", "count"),
        avg_sessions=("total_sessions", "mean"),
        avg_duration=("avg_duration", "mean"),
        avg_satisfaction=("avg_satisfaction", "mean"),
        avg_completion_rate=("completion_rate", "mean"),
    )
    .round(2)
    .reset_index()
)
print(user_type_summary.to_string(index=False))

# ── 5. Platform breakdown ─────────────────────────────────────────────────────
print("\n── Platform Breakdown ───────────────────────────────────────")
platform_summary = (
    user_retention.groupby("platform")
    .agg(
        users=("id","count"),
        avg_sessions=("total_sessions","mean"),
        avg_satisfaction=("avg_satisfaction","mean"),
    )
    .round(2)
    .reset_index()
)
print(platform_summary.to_string(index=False))

# ── Export results ────────────────────────────────────────────────────────────
topic_summary.to_csv("analyses/topic_engagement.csv", index=False)
user_retention.to_csv("analyses/user_retention.csv", index=False)
print("\n✓ Exported: analyses/topic_engagement.csv")
print("✓ Exported: analyses/user_retention.csv")
print("\nAnalysis complete! 🎉")
