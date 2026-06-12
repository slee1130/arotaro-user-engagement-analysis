-- models/facts/fct_user_retention.sql
-- One row per user with retention and engagement summary

with sessions as (
    select * from {{ ref('fct_session_metrics') }}
),

users as (
    select * from {{ ref('stg_users') }}
),

user_session_agg as (
    select
        user_id,
        count(*)                                            as total_sessions,
        count(case when is_completed then 1 end)            as completed_sessions,
        count(case when is_dropoff then 1 end)              as dropped_sessions,
        round(avg(session_duration_minutes), 2)             as avg_session_duration_minutes,
        round(avg(total_message_count), 2)                  as avg_message_count,
        round(avg(satisfaction_score), 2)                   as avg_satisfaction_score,
        min(session_started_at)                             as first_session_at,
        max(session_started_at)                             as last_session_at
    from sessions
    group by user_id
),

final as (
    select
        u.user_id,
        u.platform,
        u.locale,
        u.timezone,
        u.user_created_at,
        u.last_seen_at,

        s.total_sessions,
        s.completed_sessions,
        s.dropped_sessions,
        s.avg_session_duration_minutes,
        s.avg_message_count,
        s.avg_satisfaction_score,
        s.first_session_at,
        s.last_session_at,

        -- user type
        case
            when s.total_sessions >= 3 then 'returning'
            else 'new'
        end                                                 as user_type,

        -- retention rate
        round(
            s.completed_sessions * 100.0 / nullif(s.total_sessions, 0),
        2)                                                  as session_completion_rate,

        -- days between first and last session
        datediff('day', s.first_session_at, s.last_session_at) as days_active

    from users u
    left join user_session_agg s on u.user_id = s.user_id
)

select * from final
