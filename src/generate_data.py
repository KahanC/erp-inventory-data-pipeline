"""Deterministic, fictional ERP inventory data; no company records."""
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data'
OUT.mkdir(exist_ok=True)
rng = random.Random(42)
warehouses = [('00','Central'),('02','East'),('20','West'),('50','Online'),('51','Wholesale'),('52','Returns')]
product_codes = [('FG','Finished Goods'),('IN','Ingredients'),('CN','Containers'),('AC','Accessories'),('LT','Labels'),('SP','Spare Parts'),('MN','Manufacturing'),('FA','Food Additives'),('FC','Food Components')]
departments = [('10','Retail'),('20','Wholesale'),('30','Ecommerce')]

def write(name, fields, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

write('inventory_warehouses.csv',['whse','description'],[dict(whse=a,description=b) for a,b in warehouses])
write('inventory_product_codes.csv',['product_code','description'],[dict(product_code=a,description=b) for a,b in product_codes])
write('sales_departments.csv',['id','description'],[dict(id=a,description=b) for a,b in departments])
items=[]; uoms=[]; upcs=[]
for whse,_ in warehouses:
    for n in range(1,101):
        part=f'SKU-{n:04d}'
        pc=product_codes[(n-1)%len(product_codes)][0]
        onhand=rng.randint(0,500); committed=rng.randint(0,150)
        cost=round(rng.uniform(2,75),2)
        prices=[round(cost*x,2) for x in [1.8,1.5,1.4,1.3,1.2,1.15,1.1,1.05,1.0,1.7,1.65]]
        udf={'1st2 characters':pc[:2],'sub_type':'Standard','lead_time':str(rng.randint(3,28)), 'maxstock':str(rng.randint(400,900)), 'shelf_life':str(rng.randint(90,730)), 'flavour_type':'Assorted', 'total_cookies':'12', 'cookie_size':'25', 'net_weight':'300', 'acceptable_var':'0.05'}
        items.append(dict(whse=whse,part_no=part,description=f'Synthetic {pc} Item {n:04d}',hold=rng.choice([0,0,0,1,2]),product_code=pc,misc_1='Stock',type='Inventory',udf_data=json.dumps(udf),onhand_qty=onhand,committed_qty=committed,backorder_qty=rng.randint(0,35),purchase_qty=rng.randint(0,200),reorder_qty=rng.randint(50,180),current_cost=cost,average_cost=cost,discountable='true',last_sale_date='2026-10-15',last_receipt_date='2026-10-20',current_po=f'PO-{n:05d}',po_due_date='2026-12-01',min_buy_qty=12,uom_purchase='EA',uom_inventory='EA',sales_acct=departments[n%3][0],preferred_vendor=f'VEND-{n%12:02d}',last_year_qty=rng.randint(100,500),this_year_qty=rng.randint(100,600),next_year_qty=0,last_year_revenue=round(cost*200,2),this_year_revenue=round(cost*250,2),next_year_revenue=0))
        uoms.append(dict(whse=whse,part_no=part,uom='EA',whse_location=f'R{n%10}-B{n%20}',sell_prices='{'+','.join(map(str,prices))+'}'))
        upcs.append(dict(whse=whse,part_no=part,uom='EA',upc_code=f'{int(whse):02d}{n:010d}'))
write('inventory.csv',list(items[0]),items)
write('inventory_uoms.csv',list(uoms[0]),uoms)
write('inventory_upc_codes.csv',list(upcs[0]),upcs)
print(f'Generated {len(items)} synthetic warehouse-SKU records in {OUT}')
