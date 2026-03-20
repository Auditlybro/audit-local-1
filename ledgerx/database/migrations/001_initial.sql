-- LedgerX — Initial PostgreSQL schema
-- Multi-tenant, Tally-compatible accounting + GST

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========== MULTI-TENANT CORE ==========
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  gstin VARCHAR(15),
  pan VARCHAR(10),
  address TEXT,
  financial_year_start INTEGER NOT NULL DEFAULT 4,  -- month (4 = April)
  currency CHAR(3) NOT NULL DEFAULT 'INR',
  plan VARCHAR(50) NOT NULL DEFAULT 'free',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(255),
  role VARCHAR(50) NOT NULL DEFAULT 'user',
  org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE org_users (
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL DEFAULT 'member',
  permissions JSONB DEFAULT '[]',
  PRIMARY KEY (org_id, user_id)
);

CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  gstin VARCHAR(15),
  pan VARCHAR(10),
  cin VARCHAR(21),
  address TEXT,
  state_code CHAR(2),
  financial_year VARCHAR(9),  -- e.g. 2024-25
  logo_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_companies_org ON companies(org_id);

-- ========== MASTERS ==========
CREATE TABLE ledger_groups (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  parent_id UUID REFERENCES ledger_groups(id) ON DELETE SET NULL,
  nature VARCHAR(20) NOT NULL CHECK (nature IN ('Assets', 'Liabilities', 'Income', 'Expense')),
  is_system BOOLEAN NOT NULL DEFAULT FALSE,
  tally_name VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ledger_groups_company ON ledger_groups(company_id);
CREATE INDEX idx_ledger_groups_parent ON ledger_groups(parent_id);

CREATE TABLE ledgers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  group_id UUID NOT NULL REFERENCES ledger_groups(id) ON DELETE RESTRICT,
  name VARCHAR(255) NOT NULL,
  alias VARCHAR(255),
  opening_balance DECIMAL(18, 2) NOT NULL DEFAULT 0,
  gstin VARCHAR(15),
  pan VARCHAR(10),
  credit_limit DECIMAL(18, 2),
  tds_applicable BOOLEAN NOT NULL DEFAULT FALSE,
  bank_account_number VARCHAR(50),
  ifsc VARCHAR(11),
  contact_person VARCHAR(255),
  phone VARCHAR(20),
  email VARCHAR(255),
  address TEXT,
  state_code CHAR(2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ledgers_company ON ledgers(company_id);
CREATE INDEX idx_ledgers_group ON ledgers(group_id);
CREATE INDEX idx_ledgers_name ON ledgers(company_id, name);

CREATE TABLE stock_groups (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  parent_id UUID REFERENCES stock_groups(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stock_groups_company ON stock_groups(company_id);

CREATE TABLE units (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  symbol VARCHAR(20),
  is_compound BOOLEAN NOT NULL DEFAULT FALSE,
  base_unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
  conversion_factor DECIMAL(18, 6),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_units_company ON units(company_id);

CREATE TABLE stock_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  group_id UUID NOT NULL REFERENCES stock_groups(id) ON DELETE RESTRICT,
  name VARCHAR(255) NOT NULL,
  hsn_code VARCHAR(10),
  sac_code VARCHAR(10),
  unit VARCHAR(50),
  gst_rate DECIMAL(5, 2),
  mrp DECIMAL(18, 2),
  opening_qty DECIMAL(18, 4) NOT NULL DEFAULT 0,
  opening_value DECIMAL(18, 2) NOT NULL DEFAULT 0,
  reorder_level DECIMAL(18, 4),
  batch_tracking BOOLEAN NOT NULL DEFAULT FALSE,
  expiry_tracking BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stock_items_company ON stock_items(company_id);
CREATE INDEX idx_stock_items_group ON stock_items(group_id);

CREATE TABLE godowns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_godowns_company ON godowns(company_id);

CREATE TABLE employees (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  designation VARCHAR(100),
  department VARCHAR(100),
  pan VARCHAR(10),
  aadhaar VARCHAR(12),
  bank_account VARCHAR(50),
  joining_date DATE,
  salary_structure VARCHAR(50),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_employees_company ON employees(company_id);

-- ========== TRANSACTIONS ==========
CREATE TABLE vouchers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  voucher_type VARCHAR(50) NOT NULL,
  number VARCHAR(50),
  date DATE NOT NULL,
  party_ledger_id UUID REFERENCES ledgers(id) ON DELETE SET NULL,
  narration TEXT,
  amount DECIMAL(18, 2),
  reference VARCHAR(255),
  cost_centre VARCHAR(100),
  is_optional BOOLEAN NOT NULL DEFAULT FALSE,
  is_cancelled BOOLEAN NOT NULL DEFAULT FALSE,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  tally_guid VARCHAR(100),
  source VARCHAR(20) NOT NULL DEFAULT 'manual' CHECK (source IN ('manual', 'import', 'api'))
);

CREATE INDEX idx_vouchers_company ON vouchers(company_id);
CREATE INDEX idx_vouchers_date ON vouchers(company_id, date);
CREATE INDEX idx_vouchers_type ON vouchers(company_id, voucher_type);
CREATE INDEX idx_vouchers_party ON vouchers(party_ledger_id);

CREATE TABLE voucher_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  voucher_id UUID NOT NULL REFERENCES vouchers(id) ON DELETE CASCADE,
  ledger_id UUID NOT NULL REFERENCES ledgers(id) ON DELETE RESTRICT,
  dr_amount DECIMAL(18, 2) NOT NULL DEFAULT 0,
  cr_amount DECIMAL(18, 2) NOT NULL DEFAULT 0,
  narration TEXT,
  bill_ref VARCHAR(255),
  cost_centre VARCHAR(100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_voucher_entries_voucher ON voucher_entries(voucher_id);
CREATE INDEX idx_voucher_entries_ledger ON voucher_entries(ledger_id);

CREATE TABLE invoice_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  voucher_id UUID NOT NULL REFERENCES vouchers(id) ON DELETE CASCADE,
  stock_item_id UUID REFERENCES stock_items(id) ON DELETE SET NULL,
  godown_id UUID REFERENCES godowns(id) ON DELETE SET NULL,
  batch VARCHAR(100),
  expiry_date DATE,
  quantity DECIMAL(18, 4) NOT NULL,
  rate DECIMAL(18, 2) NOT NULL,
  unit VARCHAR(50),
  discount_pct DECIMAL(5, 2) DEFAULT 0,
  discount_amount DECIMAL(18, 2) DEFAULT 0,
  taxable_value DECIMAL(18, 2) NOT NULL,
  cgst_rate DECIMAL(5, 2) DEFAULT 0,
  cgst_amount DECIMAL(18, 2) DEFAULT 0,
  sgst_rate DECIMAL(5, 2) DEFAULT 0,
  sgst_amount DECIMAL(18, 2) DEFAULT 0,
  igst_rate DECIMAL(5, 2) DEFAULT 0,
  igst_amount DECIMAL(18, 2) DEFAULT 0,
  total_amount DECIMAL(18, 2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoice_items_voucher ON invoice_items(voucher_id);

-- ========== GST ==========
CREATE TABLE gst_returns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  return_type VARCHAR(20) NOT NULL,
  period VARCHAR(10) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'draft',
  filed_at TIMESTAMPTZ,
  json_data JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_gst_returns_company ON gst_returns(company_id);
CREATE INDEX idx_gst_returns_period ON gst_returns(company_id, period);

CREATE TABLE einvoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  voucher_id UUID NOT NULL REFERENCES vouchers(id) ON DELETE CASCADE,
  irn VARCHAR(100),
  ack_no VARCHAR(100),
  ack_date TIMESTAMPTZ,
  qr_code TEXT,
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  cancelled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_einvoices_voucher ON einvoices(voucher_id);

CREATE TABLE ewaybills (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  voucher_id UUID NOT NULL REFERENCES vouchers(id) ON DELETE CASCADE,
  ewb_no VARCHAR(50),
  generated_at TIMESTAMPTZ,
  valid_till TIMESTAMPTZ,
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ewaybills_voucher ON ewaybills(voucher_id);

CREATE TABLE gst_notices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  notice_ref VARCHAR(100),
  notice_type VARCHAR(100),
  section VARCHAR(50),
  period VARCHAR(20),
  amount_demanded DECIMAL(18, 2),
  deadline DATE,
  status VARCHAR(30) NOT NULL DEFAULT 'open',
  notice_text TEXT,
  reply_text TEXT,
  filed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_gst_notices_company ON gst_notices(company_id);

-- ========== BANKING ==========
CREATE TABLE bank_accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ledger_id UUID NOT NULL REFERENCES ledgers(id) ON DELETE CASCADE UNIQUE,
  account_number VARCHAR(50) NOT NULL,
  ifsc VARCHAR(11),
  bank_name VARCHAR(255),
  branch VARCHAR(255),
  account_type VARCHAR(50),
  opening_balance DECIMAL(18, 2) NOT NULL DEFAULT 0,
  reconciled_till DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bank_accounts_ledger ON bank_accounts(ledger_id);

CREATE TABLE bank_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  bank_account_id UUID NOT NULL REFERENCES bank_accounts(id) ON DELETE CASCADE,
  transaction_date DATE NOT NULL,
  value_date DATE,
  description TEXT,
  debit DECIMAL(18, 2) NOT NULL DEFAULT 0,
  credit DECIMAL(18, 2) NOT NULL DEFAULT 0,
  balance DECIMAL(18, 2),
  reconciled BOOLEAN NOT NULL DEFAULT FALSE,
  voucher_id UUID REFERENCES vouchers(id) ON DELETE SET NULL,
  imported_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bank_transactions_account ON bank_transactions(bank_account_id);
CREATE INDEX idx_bank_transactions_date ON bank_transactions(bank_account_id, transaction_date);

-- ========== IMPORTS ==========
CREATE TABLE import_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  source_type VARCHAR(50) NOT NULL,
  file_name VARCHAR(255),
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  total_records INTEGER DEFAULT 0,
  imported_records INTEGER DEFAULT 0,
  error_records INTEGER DEFAULT 0,
  errors_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_import_sessions_company ON import_sessions(company_id);

-- ========== ROW LEVEL SECURITY (multi-tenant) ==========
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledgers ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE units ENABLE ROW LEVEL SECURITY;
ALTER TABLE godowns ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE vouchers ENABLE ROW LEVEL SECURITY;
ALTER TABLE voucher_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE gst_returns ENABLE ROW LEVEL SECURITY;
ALTER TABLE einvoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE ewaybills ENABLE ROW LEVEL SECURITY;
ALTER TABLE gst_notices ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: users see only their org's data (application sets current_setting('app.current_org_id'))
CREATE POLICY org_isolation_orgs ON organizations
  FOR ALL USING (id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY org_isolation_companies ON companies
  FOR ALL USING (org_id = current_setting('app.current_org_id', true)::UUID);

CREATE POLICY org_isolation_ledger_groups ON ledger_groups
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_ledgers ON ledgers
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_vouchers ON vouchers
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_stock_groups ON stock_groups
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_stock_items ON stock_items
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_units ON units
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_godowns ON godowns
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_employees ON employees
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_voucher_entries ON voucher_entries
  FOR ALL USING (voucher_id IN (SELECT id FROM vouchers WHERE company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID)));

CREATE POLICY org_isolation_invoice_items ON invoice_items
  FOR ALL USING (voucher_id IN (SELECT id FROM vouchers WHERE company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID)));

CREATE POLICY org_isolation_gst_returns ON gst_returns
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_einvoices ON einvoices
  FOR ALL USING (voucher_id IN (SELECT id FROM vouchers WHERE company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID)));

CREATE POLICY org_isolation_ewaybills ON ewaybills
  FOR ALL USING (voucher_id IN (SELECT id FROM vouchers WHERE company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID)));

CREATE POLICY org_isolation_gst_notices ON gst_notices
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

CREATE POLICY org_isolation_bank_accounts ON bank_accounts
  FOR ALL USING (ledger_id IN (SELECT id FROM ledgers WHERE company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID)));

CREATE POLICY org_isolation_bank_transactions ON bank_transactions
  FOR ALL USING (bank_account_id IN (SELECT id FROM bank_accounts WHERE ledger_id IN (SELECT id FROM ledgers WHERE company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID))));

CREATE POLICY org_isolation_import_sessions ON import_sessions
  FOR ALL USING (company_id IN (SELECT id FROM companies WHERE org_id = current_setting('app.current_org_id', true)::UUID));

-- Users: allow access to self and org members (app sets app.current_user_id)
CREATE POLICY user_org_access ON users
  FOR ALL USING (org_id = current_setting('app.current_org_id', true)::UUID OR id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY org_users_org_access ON org_users
  FOR ALL USING (org_id = current_setting('app.current_org_id', true)::UUID);
