"""
Arotaro Mock Data Generator
Generates synthetic data based on real Arotaro DB schema
"""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────
NUM_USERS    = 1000
NUM_SESSIONS = 2800
START_DATE   = datetime(2024, 1, 1)
END_DATE     = datetime(2025, 6, 1)

TOPICS       = ["relationship", "career", "family", "anxiety", "general", "self-growth"]
PLATFORMS    = ["ios", "android"]
LOCALES      = ["en", "ko", "ja", "zh"]
TIMEZONES    = ["America/Vancouver", "America/Toronto", "Asia/Seoul", "Asia/Tokyo"]
STATUSES     = ["SESSION_END", "WRAP_UP", "COUNSELLING", "QUESTIONING"]

# ── Helpers ──────────────────────────────────────────────────────────────────
def rand_date(start, end):
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta))

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path}  ({len(rows)} rows)")

# ── 1. concerned_user ────────────────────────────────────────────────────────
users = []
for i in range(1, NUM_USERS + 1):
    created = rand_date(START_DATE, END_DATE)
    users.append({
        "id":         i,
        "email":      f"user{i}@example.com",
        "created_at": created.isoformat(),
        "updated_at": created.isoformat(),
    })

# ── 2. user_devices ──────────────────────────────────────────────────────────
devices = []
for u in users:
    platform  = random.choice(PLATFORMS)
    locale    = random.choice(LOCALES)
    timezone  = random.choice(TIMEZONES)
    last_seen = rand_date(datetime.fromisoformat(u["created_at"]), END_DATE)
    devices.append({
        "id":              u["id"],
        "user_id":         u["id"],
        "device_id":       f"device_{u['id']}_{random.randint(1000,9999)}",
        "platform":        platform,
        "locale":          locale,
        "timezone":        timezone,
        "last_seen_at":    last_seen.isoformat(),
        "created_at":      u["created_at"],
        "updated_at":      u["created_at"],
    })

# ── 3. conversation_session ───────────────────────────────────────────────────
sessions = []
session_id = 1
user_session_counts = {}

for _ in range(NUM_SESSIONS):
    # weight returning users slightly more
    user = random.choice(users)
    uid  = user["id"]
    user_session_counts[uid] = user_session_counts.get(uid, 0) + 1

    topic          = random.choice(TOPICS)
    is_dropoff     = random.random() < 0.20          # ~20% drop-off
    status         = "COUNSELLING" if is_dropoff else random.choice(["SESSION_END", "WRAP_UP"])

    # session length by topic (mirrors existing analysis)
    base_duration = {
        "career": 1140, "relationship": 1020, "anxiety": 960,
        "family": 900,  "self-growth": 840,  "general": 720,
    }[topic]
    timer_duration = max(300, int(random.gauss(base_duration, 200)))

    created = rand_date(START_DATE, END_DATE)
    updated = created + timedelta(seconds=timer_duration)

    sessions.append({
        "id":              session_id,
        "concerned_user_id": uid,
        "status":          status,
        "timer_duration":  timer_duration,
        "topic":           topic,
        "reader_name":     f"Oracle_{random.randint(1,5)}",
        "is_dropoff":      is_dropoff,
        "created_at":      created.isoformat(),
        "updated_at":      updated.isoformat(),
    })
    session_id += 1

# ── 4. conversation_message ───────────────────────────────────────────────────
messages = []
msg_id = 1

for s in sessions:
    # longer sessions → more messages; drop-off sessions → fewer
    if s["is_dropoff"]:
        num_msgs = random.randint(2, 8)
    else:
        base = max(6, int(s["timer_duration"] / 120))
        num_msgs = random.randint(base, base + 10)

    session_start = datetime.fromisoformat(s["created_at"])
    interval      = s["timer_duration"] / max(num_msgs, 1)

    for j in range(num_msgs):
        conversant  = "HUMAN" if j % 2 == 0 else "AI"
        msg_time    = session_start + timedelta(seconds=interval * j)
        satisfaction = None
        if conversant == "HUMAN" and j == num_msgs - 1:
            # satisfaction roughly correlated with message count
            satisfaction = min(5, max(1, round(random.gauss(3.5 + num_msgs * 0.05, 0.8), 1)))

        messages.append({
            "id":                     msg_id,
            "conversation_session_id": s["id"],
            "concerned_user_id":       s["concerned_user_id"],
            "conversant":              conversant,
            "satisfaction_score":      satisfaction,
            "created_at":              msg_time.isoformat(),
            "updated_at":              msg_time.isoformat(),
        })
        msg_id += 1

# ── Write CSVs ────────────────────────────────────────────────────────────────
print("\nGenerating seed CSVs…")
write_csv("seeds/concerned_users.csv",       users,    ["id","email","created_at","updated_at"])
write_csv("seeds/user_devices.csv",          devices,  ["id","user_id","device_id","platform","locale","timezone","last_seen_at","created_at","updated_at"])
write_csv("seeds/conversation_sessions.csv", sessions, ["id","concerned_user_id","status","timer_duration","topic","reader_name","is_dropoff","created_at","updated_at"])
write_csv("seeds/conversation_messages.csv", messages, ["id","conversation_session_id","concerned_user_id","conversant","satisfaction_score","created_at","updated_at"])
print("\nDone! 🎉")
