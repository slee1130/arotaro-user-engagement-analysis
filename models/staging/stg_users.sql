-- models/staging/stg_users.sql
-- Cleans and standardizes raw concerned_user + device data

with users as (
    select * from {{ ref('concerned_users') }}
),

devices as (
    select * from {{ ref('user_devices') }}
),

joined as (
    select
        u.id                                        as user_id,
        u.email,
        cast(u.created_at as timestamp)             as user_created_at,

        -- device info
        d.platform,
        d.locale,
        d.timezone,
        cast(d.last_seen_at as timestamp)           as last_seen_at,

        -- days since signup
        datediff('day',
            cast(u.created_at as timestamp),
            cast(d.last_seen_at as timestamp)
        )                                           as days_since_signup

    from users u
    left join devices d on u.id = d.user_id
)

select * from joined
