-- Clean, typed view over raw transactions.
select
    transaction_id,
    merchant_id,
    lower(merchant_category)           as merchant_category,
    upper(country)                     as country,
    lower(card_type)                   as card_type,
    cast(amount_usd as decimal(12, 2)) as amount_usd,
    lower(status)                      as status,
    cast(is_disputed as boolean)       as is_disputed,
    cast(risk_score as integer)        as risk_score,
    cast(created_at as timestamp)      as created_at,
    cast(created_at as date)           as created_date
from {{ source('raw', 'transactions') }}
