\set ON_ERROR_STOP on
\copy inventory_warehouses FROM '/tmp/erp-data/inventory_warehouses.csv' WITH (FORMAT csv, HEADER true)
\copy inventory_product_codes FROM '/tmp/erp-data/inventory_product_codes.csv' WITH (FORMAT csv, HEADER true)
\copy sales_departments FROM '/tmp/erp-data/sales_departments.csv' WITH (FORMAT csv, HEADER true)
\copy inventory FROM '/tmp/erp-data/inventory.csv' WITH (FORMAT csv, HEADER true)
\copy inventory_uoms FROM '/tmp/erp-data/inventory_uoms.csv' WITH (FORMAT csv, HEADER true)
\copy inventory_upc_codes FROM '/tmp/erp-data/inventory_upc_codes.csv' WITH (FORMAT csv, HEADER true)
