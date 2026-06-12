-- models/staging/stg_sessions.sql
-- Cleans and standardizes raw conversation_session data

with source as (
    select * from {{ ref('conversation_sessions') }}
),

renamed as (
    select
        id                                          as session_id,
        concerned_user_id                           as user_id,
        status,
        topic,
        reader_name,
        timer_duration,
        is_dropoff,
        cast(created_at as timestamp)               as session_started_at,
        cast(updated_at as timestamp)               as session_ended_at,

        -- session length in minutes
        round(timer_duration / 60.0, 2)             as session_duration_minutes,

        -- is session completed?
        case
            when status in ('SESSION_END', 'WRAP_UP') then true
            else false
        end                                         as is_completed

    from source
)

select * from renamed
