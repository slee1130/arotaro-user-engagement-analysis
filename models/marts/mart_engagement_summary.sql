-- models/marts/mart_engagement_summary.sql
-- Final reporting layer: aggregated engagement metrics by topic and user type
-- This is what Tableau connects to

with session_metrics as (
    select * from {{ ref('fct_session_metrics') }}
),

user_retention as (
    select * from {{ ref('fct_user_retention') }}
),

-- Topic-level engagement
topic_summary as (
    select
        topic,
        count(*)                                            as total_sessions,
        round(avg(session_duration_minutes), 2)             as avg_duration_minutes,
        round(avg(total_message_count), 2)                  as avg_message_count,
        round(avg(satisfaction_score), 2)                   as avg_satisfaction,
        round(sum(case when is_dropoff then 1 else 0 end) * 100.0 / count(*), 2) as dropoff_rate_pct,
        round(sum(case when is_completed then 1 else 0 end) * 100.0 / count(*), 2) as completion_rate_pct
    from session_metrics
    group by topic
),

-- User type comparison
user_type_summary as (
    select
        user_type,
        count(*)                                            as total_users,
        round(avg(avg_session_duration_minutes), 2)         as avg_session_duration,
        round(avg(avg_satisfaction_score), 2)               as avg_satisfaction,
        round(avg(session_completion_rate), 2)              as avg_completion_rate,
        round(avg(total_sessions), 2)                       as avg_sessions_per_user
    from user_retention
    where user_type is not null
    group by user_type
)

-- Final mart: topic-level (Tableau main view)
select
    t.topic,
    t.total_sessions,
    t.avg_duration_minutes,
    t.avg_message_count,
    t.avg_satisfaction,
    t.dropoff_rate_pct,
    t.completion_rate_pct
from topic_summary t
order by t.avg_duration_minutes desc
