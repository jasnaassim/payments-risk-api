-- One-time Snowflake setup for the raw layer.
-- Run in a worksheet or with SnowSQL. Adjust names to your account.

create warehouse if not exists risk_wh
  warehouse_size = 'XSMALL' auto_suspend = 60 auto_resume = true;

create database if not exists payments_risk;
create schema if not exists payments_risk.raw;
create schema if not exists payments_risk.analytics;

use schema payments_risk.raw;

create or replace file format csv_ff
  type = csv skip_header = 1 field_optionally_enclosed_by = '"';

create or replace stage transactions_stage file_format = csv_ff;

create or replace table transactions (
  transaction_id    varchar,
  merchant_id       varchar,
  merchant_category varchar,
  country           varchar,
  card_type         varchar,
  amount_usd        number(12, 2),
  status            varchar,
  is_disputed       boolean,
  risk_score        number(5, 0),
  created_at        timestamp_ntz
);

-- From SnowSQL:
--   put file://data/transactions.csv @transactions_stage auto_compress = true;
copy into transactions from @transactions_stage on_error = 'abort_statement';
