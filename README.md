# Arotaro User Engagement & Retention Analysis

## Overview

End-to-end analytics engineering project built on top of **Arotaro**, an AI-based emotional support application with 1,000+ real users.

This project extends the original Tableau analysis by introducing a full **dbt data modeling layer**, transforming raw application data into clean, testable, and documented analytics models.

---

## Architecture

```
Raw Seed Data (CSV)
        │
        ▼
┌─────────────────────┐
│   Staging Layer     │  stg_sessions, stg_messages, stg_users
│   (dbt views)       │  → clean, rename, cast types
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    Facts Layer      │  fct_session_metrics, fct_user_retention
│    (dbt tables)     │  → aggregate, join, business logic
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    Marts Layer      │  mart_engagement_summary
│    (dbt tables)     │  → final reporting models for Tableau
└────────┬────────────┘
         │
         ▼
  Tableau Dashboard  +  Pandas Analysis (Jupyter)
```

---

## Tools Used

| Tool        | Purpose                            |
|-------------|------------------------------------|
| **dbt**     | Data modeling, testing, documentation |
| **Python**  | Mock data generation               |
| **Pandas**  | Exploratory data analysis          |
| **Tableau** | Dashboard & visualization          |
| **SQL**     | All transformation logic           |

---

## Project Structure

```
arotaro/
├── seeds/                          # Mock data CSVs (based on real schema)
│   ├── concerned_users.csv
│   ├── user_devices.csv
│   ├── conversation_sessions.csv
│   └── conversation_messages.csv
│
├── models/
│   ├── staging/                    # Clean raw data
│   │   ├── stg_sessions.sql
│   │   ├── stg_messages.sql
│   │   └── stg_users.sql
│   ├── facts/                      # Business logic
│   │   ├── fct_session_metrics.sql
│   │   └── fct_user_retention.sql
│   └── marts/                      # Reporting layer
│       └── mart_engagement_summary.sql
│
├── analyses/
│   └── engagement_analysis.py      # Pandas EDA
│
├── generate_mock_data.py           # Synthetic data generator
├── dbt_project.yml
└── models/schema.yml               # dbt tests + documentation
```

---

## Key Findings

### 1. Topic-Level Engagement
| Topic        | Avg Duration | Avg Messages | Drop-off Rate |
|--------------|-------------|--------------|---------------|
| Career       | 19.2 min    | 12.5         | 20%           |
| Relationship | 17.0 min    | 11.4         | 19%           |
| Anxiety      | 16.2 min    | 10.9         | 23%           |
| General      | 12.4 min    | 10.0         | 22%           |

→ **Career and relationship topics drive the highest engagement**

### 2. Retention
- Overall drop-off rate: **~21%** (80% engaged)
- Returning users (3+ sessions): **57%** of user base
- Returning users show marginally higher completion rates (79.7% vs 77.7%)

### 3. Satisfaction
- Satisfaction generally increases with message count
- Avg satisfaction score: **4.0 / 5.0**

---

## dbt Models

### Staging
- `stg_sessions` — cleans session data, calculates duration in minutes, flags completed sessions
- `stg_messages` — standardizes messages, adds human/AI flag
- `stg_users` — joins user profiles with device info

### Facts
- `fct_session_metrics` — one row per session; message counts, satisfaction, composite engagement score
- `fct_user_retention` — one row per user; retention metrics, user type (new vs returning), days active

### Marts
- `mart_engagement_summary` — final reporting layer aggregated by topic; feeds Tableau dashboard

---

## dbt Tests
All models include schema tests:
- `unique` + `not_null` on all primary keys
- `accepted_values` on status, topic, conversant, user_type columns
- Referential integrity between sessions and messages

---

## How to Run

```bash
# Generate mock data
python generate_mock_data.py

# Run dbt models
dbt seed
dbt run
dbt test

# Run Pandas analysis
python analyses/engagement_analysis.py
```
