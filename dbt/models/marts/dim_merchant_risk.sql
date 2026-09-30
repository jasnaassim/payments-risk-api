-- One row per merchant with window-level risk metrics and a high-risk flag.
with agg as (
    select
        merchant_id,
        max(merchant_category)                                         as merchant_category,
        count(*)                                                       as txn_count,
        sum(case when status = 'succeeded' then amount_usd else 0 end) as gross_volume_usd,
        sum(case when status = 'declined' then 1 else 0 end) * 1.0
            / count(*)                                                 as decline_rate,
        sum(case when is_disputed then 1 else 0 end) * 1.0
            / nullif(sum(case when status = 'succeeded' then 1 else 0 end), 0)
                                                                       as dispute_rate,
        avg(risk_score)                                                as avg_risk_score,
        min(created_date)                                              as first_seen,
        max(created_date)                                              as last_seen
    from {{ ref('stg_transactions') }}
    group by merchant_id
)

select
    *,
    case
        when txn_count >= {{ var('min_transactions_for_flag') }}
         and dispute_rate >= {{ var('high_risk_dispute_rate') }}
        then true else false
    end as is_high_risk
from agg
