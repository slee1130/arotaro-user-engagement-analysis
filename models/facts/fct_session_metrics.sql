-- models/facts/fct_session_metrics.sql
-- One row per session with aggregated message and satisfaction metrics

with sessions as (
    select * from {{ ref('stg_sessions') }}
),

messages as (
    select * from {{ ref('stg_messages') }}
),

message_agg as (
    select
        session_id,
        count(*)                                            as total_message_count,
        count(case when is_human_message then 1 end)        as human_message_count,
        count(case when not is_human_message then 1 end)    as ai_message_count,
        max(satisfaction_score)                             as satisfaction_score
    from messages
    group by session_id
),

final as (
    select
        s.session_id,
        s.user_id,
        s.topic,
        s.status,
        s.is_dropoff,
        s.is_completed,
        s.session_duration_minutes,
        s.session_started_at,
        s.session_ended_at,

        m.total_message_count,
        m.human_message_count,
        m.ai_message_count,
        m.satisfaction_score,

        -- engagement score (simple composite)
        round(
            (s.session_duration_minutes * 0.5) +
            (coalesce(m.total_message_count, 0) * 0.3) +
            (coalesce(m.satisfaction_score, 3) * 0.2),
        2)                                                  as engagement_score

    from sessions s
    left join message_agg m on s.session_id = m.session_id
)

select * from final
