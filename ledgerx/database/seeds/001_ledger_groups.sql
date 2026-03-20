-- LedgerX — Seed 28 Tally-compatible ledger groups
-- Run after 001_initial.sql. Uses a template company; replace company_id for your org or copy on company create.

-- Template org and company for seed (optional: skip if you already have a company)
INSERT INTO organizations (id, name, financial_year_start, currency, plan)
VALUES ('a0000000-0000-0000-0000-000000000001', 'LedgerX Template', 4, 'INR', 'free')
ON CONFLICT (id) DO NOTHING;

INSERT INTO companies (id, org_id, name, financial_year)
VALUES (
  'b0000000-0000-0000-0000-000000000001',
  'a0000000-0000-0000-0000-000000000001',
  'Default Company',
  '2024-25'
)
ON CONFLICT (id) DO NOTHING;

-- Step 1: Insert 19 primary ledger groups
INSERT INTO ledger_groups (id, company_id, name, parent_id, nature, is_system, tally_name)
VALUES
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Capital Account', NULL, 'Liabilities', TRUE, 'Capital Account'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Reserves & Surplus', NULL, 'Liabilities', TRUE, 'Reserves & Surplus'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Loans (Liability)', NULL, 'Liabilities', TRUE, 'Loans (Liability)'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Secured Loans', NULL, 'Liabilities', TRUE, 'Secured Loans'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Unsecured Loans', NULL, 'Liabilities', TRUE, 'Unsecured Loans'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Current Liabilities', NULL, 'Liabilities', TRUE, 'Current Liabilities'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Provisions', NULL, 'Liabilities', TRUE, 'Provisions'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Suspense Account', NULL, 'Liabilities', TRUE, 'Suspense Account'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Fixed Assets', NULL, 'Assets', TRUE, 'Fixed Assets'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Investments', NULL, 'Assets', TRUE, 'Investments'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Current Assets', NULL, 'Assets', TRUE, 'Current Assets'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Loans & Advances', NULL, 'Assets', TRUE, 'Loans & Advances'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Misc Expenses Asset', NULL, 'Assets', TRUE, 'Misc. Expenses (Asset)'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Sales Accounts', NULL, 'Income', TRUE, 'Sales Accounts'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Direct Income', NULL, 'Income', TRUE, 'Direct Incomes'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Indirect Income', NULL, 'Income', TRUE, 'Indirect Incomes'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Purchase Accounts', NULL, 'Expense', TRUE, 'Purchase Accounts'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Direct Expenses', NULL, 'Expense', TRUE, 'Direct Expenses'),
  (uuid_generate_v4(), 'b0000000-0000-0000-0000-000000000001', 'Indirect Expenses', NULL, 'Expense', TRUE, 'Indirect Expenses');

-- Step 2: Sub-groups (parent = Current Liabilities or Current Assets)
INSERT INTO ledger_groups (company_id, name, parent_id, nature, is_system, tally_name)
SELECT 'b0000000-0000-0000-0000-000000000001', name, parent_id, nature, TRUE, tally_name
FROM (VALUES
  ('Sundry Creditors', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Liabilities'), 'Liabilities', 'Sundry Creditors'),
  ('Duties & Taxes', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Liabilities'), 'Liabilities', 'Duties & Taxes'),
  ('Bank OD Accounts', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Liabilities'), 'Liabilities', 'Bank OD A/c'),
  ('Bank OCC Accounts', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Liabilities'), 'Liabilities', 'Bank OCC A/c'),
  ('Sundry Debtors', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Assets'), 'Assets', 'Sundry Debtors'),
  ('Cash-in-Hand', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Assets'), 'Assets', 'Cash-in-Hand'),
  ('Bank Accounts', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Assets'), 'Assets', 'Bank Accounts'),
  ('Stock-in-Hand', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Assets'), 'Assets', 'Stock-in-Hand'),
  ('Deposits (Asset)', (SELECT id FROM ledger_groups WHERE company_id = 'b0000000-0000-0000-0000-000000000001' AND name = 'Current Assets'), 'Assets', 'Deposits (Asset)')
) AS t(name, parent_id, nature, tally_name);
