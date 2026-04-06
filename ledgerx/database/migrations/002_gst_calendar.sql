-- GST calendar: longer period keys + unique filing row per company/type/period
ALTER TABLE gst_returns ALTER COLUMN period TYPE VARCHAR(32);

CREATE UNIQUE INDEX IF NOT EXISTS uq_gst_returns_company_type_period
  ON gst_returns (company_id, return_type, period);
