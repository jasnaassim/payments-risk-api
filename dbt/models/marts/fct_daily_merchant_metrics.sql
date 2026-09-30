-- One row per merchant per day. Counts are stored alongside rates so
-- rates can be re-aggregated correctly (never average a rate).
with daily as (
    select
        created_date                                                   as metric_date,
        merchant_id,
        count(*)                                                       as txn_count,
        sum(case when status = 'succeeded' then 1 else 0 end)          as succeeded_count,
        sum(case when status = 'declined' then 1 else 0 end)           as declined_count,
        sum(case when status = 'refunded' then 1 else 0 end)           as refunded_count,
        sum(case when is_disputed then 1 else 0 end)                   as disputed_count,
        sum(case when status = 'succeeded' then amount_usd else 0 end) as gross_volume_usd,
        avg(risk_score)                                                as avg_risk_score
    from {{ ref('stg_transactions') }}
    group by 1, 2
)

select
    *,
    declined_count * 1.0 / txn_count                  as decline_rate,
    refunded_count * 1.0 / txn_count                  as refund_rate,
    disputed_count * 1.0 / nullif(succeeded_count, 0) as dispute_rate
from daily
