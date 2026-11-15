CREATE TABLE IF NOT EXISTS inventory_warehouses (whse text PRIMARY KEY, description text NOT NULL);
CREATE TABLE IF NOT EXISTS inventory_product_codes (product_code text PRIMARY KEY, description text NOT NULL);
CREATE TABLE IF NOT EXISTS sales_departments (id text PRIMARY KEY, description text NOT NULL);
CREATE TABLE IF NOT EXISTS inventory (
 whse text NOT NULL REFERENCES inventory_warehouses(whse), part_no text NOT NULL,
 description text NOT NULL, hold integer NOT NULL DEFAULT 0 CHECK (hold BETWEEN 0 AND 2),
 product_code text NOT NULL REFERENCES inventory_product_codes(product_code),
 misc_1 text, type text, udf_data jsonb NOT NULL DEFAULT '{}'::jsonb,
 onhand_qty numeric(14,2) NOT NULL DEFAULT 0, committed_qty numeric(14,2) NOT NULL DEFAULT 0,
 backorder_qty numeric(14,2) NOT NULL DEFAULT 0, purchase_qty numeric(14,2) NOT NULL DEFAULT 0,
 reorder_qty numeric(14,2) NOT NULL DEFAULT 0, current_cost numeric(14,2), average_cost numeric(14,2),
 discountable boolean DEFAULT true, last_sale_date date, last_receipt_date date,
 current_po text, po_due_date date, min_buy_qty numeric(14,2),
 uom_purchase text DEFAULT 'EA', uom_inventory text DEFAULT 'EA',
 sales_acct text REFERENCES sales_departments(id), preferred_vendor text,
 last_year_qty numeric(14,2), this_year_qty numeric(14,2), next_year_qty numeric(14,2),
 last_year_revenue numeric(14,2), this_year_revenue numeric(14,2), next_year_revenue numeric(14,2),
 PRIMARY KEY (whse, part_no));
CREATE TABLE IF NOT EXISTS inventory_uoms (
 whse text NOT NULL, part_no text NOT NULL, uom text NOT NULL,
 whse_location text, sell_prices numeric(14,2)[] NOT NULL DEFAULT '{}'::numeric[],
 PRIMARY KEY (whse,part_no,uom), FOREIGN KEY (whse,part_no) REFERENCES inventory(whse,part_no));
CREATE TABLE IF NOT EXISTS inventory_upc_codes (
 whse text NOT NULL, part_no text NOT NULL, uom text NOT NULL, upc_code text NOT NULL,
 PRIMARY KEY (whse,part_no,uom), FOREIGN KEY (whse,part_no) REFERENCES inventory(whse,part_no));
