-- Fails if any rate falls outside [0, 1].
select *
from {{ ref('fct_daily_merchant_metrics') }}
where decline_rate not between 0 and 1
   or refund_rate  not between 0 and 1
   or coalesce(dispute_rate, 0) not between 0 and 1
