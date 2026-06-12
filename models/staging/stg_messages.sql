-- models/staging/stg_messages.sql
-- Cleans and standardizes raw conversation_message data

with source as (
    select * from {{ ref('conversation_messages') }}
),

renamed as (
    select
        id                                          as message_id,
        conversation_session_id                     as session_id,
        concerned_user_id                           as user_id,
        conversant,
        satisfaction_score,
        cast(created_at as timestamp)               as sent_at,

        -- is this a human message?
        case when conversant = 'HUMAN' then true else false end as is_human_message

    from source
)

select * from renamed
