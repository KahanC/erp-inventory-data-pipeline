"""Generate a static, interactive Plotly dashboard from the validated DuckDB mart."""
from pathlib import Path
from html import escape
import json
import duckdb
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'erp_inventory.duckdb'
DEST = ROOT / 'docs' / 'index.html'


def records(con, query):
    result = con.execute(query)
    keys = [col[0] for col in result.description]
    return [dict(zip(keys, row)) for row in result.fetchall()]


def build_dashboard():
    if not DB.exists():
        raise FileNotFoundError('Database missing: run python src/pipeline.py first')
    with duckdb.connect(str(DB), read_only=True) as con:
        n = con.execute('SELECT COUNT(*) FROM inventory_mart').fetchone()[0]
        if n == 0:
            raise ValueError('Empty mart; refusing to publish dashboard')
        wh = records(con, (ROOT/'sql'/'04_dashboard_aggregates.sql').read_text())
        groups = records(con, """SELECT product_group, COUNT(*) AS sku_count,
            ROUND(SUM(extended_inventory_value),2) AS inventory_value,
            SUM(CASE WHEN below_reorder_point THEN 1 ELSE 0 END) AS below_rop
            FROM inventory_mart GROUP BY product_group ORDER BY inventory_value DESC""")
        status = records(con, """SELECT inventory_status, COUNT(*) AS sku_count
            FROM inventory_mart GROUP BY inventory_status ORDER BY sku_count DESC""")
        risks = records(con, """SELECT whse, part_no, product_group, available_qty,
            reorder_point, projected_available_qty, extended_inventory_value
            FROM inventory_mart WHERE below_reorder_point
            ORDER BY (reorder_point - available_qty) DESC, whse, part_no LIMIT 12""")
        totals = records(con, """SELECT COUNT(*) AS skus,
            ROUND(SUM(extended_inventory_value),2) AS value,
            SUM(CASE WHEN below_reorder_point THEN 1 ELSE 0 END) AS below_rop,
            SUM(CASE WHEN available_qty < 0 THEN 1 ELSE 0 END) AS shortages
            FROM inventory_mart""")[0]

    colors = {'navy':'#11233e','blue':'#4c88f6','teal':'#36c7b5','gold':'#f4b860','red':'#ef7181'}
    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        'Inventory value by warehouse', 'Inventory value by product group',
        'Stock availability by warehouse', 'Inventory status mix'),
        specs=[[{'type':'bar'},{'type':'bar'}],[{'type':'bar'},{'type':'domain'}]],
        vertical_spacing=.19, horizontal_spacing=.14)
    fig.add_trace(go.Bar(x=[x['warehouse_name'] for x in wh], y=[float(x['inventory_value']) for x in wh],
        marker_color=colors['blue'], name='Inventory value', hovertemplate='%{x}<br>$%{y:,.2f}<extra></extra>'),row=1,col=1)
    fig.add_trace(go.Bar(x=[x['product_group'] for x in groups],y=[float(x['inventory_value']) for x in groups],
        marker_color=colors['teal'],name='Product group value',hovertemplate='%{x}<br>$%{y:,.2f}<extra></extra>'),row=1,col=2)
    fig.add_trace(go.Bar(x=[x['warehouse_name'] for x in wh],y=[float(x['available_units']) for x in wh],
        marker_color=[colors['red'] if float(x['available_units'])<0 else colors['blue'] for x in wh],
        name='Available units',hovertemplate='%{x}<br>%{y:,.0f} units<extra></extra>'),row=2,col=1)
    fig.add_trace(go.Pie(labels=[x['inventory_status'] for x in status],values=[x['sku_count'] for x in status],
        hole=.62,marker_colors=[colors['teal'],colors['gold'],colors['red']],name='Inventory status',
        textinfo='label+percent'),row=2,col=2)
    fig.update_layout(template='plotly_white',height=820,margin=dict(l=45,r=35,t=75,b=65),
        paper_bgcolor='#ffffff',plot_bgcolor='#ffffff',font=dict(family='Arial, sans-serif',color=colors['navy']),
        showlegend=False,bargap=.25)
    fig.update_xaxes(tickangle=-28, row=1,col=2)
    fig.update_yaxes(tickprefix='$',tickformat=',.0f',row=1,col=1)
    fig.update_yaxes(tickprefix='$',tickformat=',.0f',row=1,col=2)
    graph=fig.to_html(full_html=False,include_plotlyjs=True,config={'responsive':True,'displaylogo':False})
    def fmt(v): return f'{int(v):,}'
    def money(v): return f'${float(v):,.0f}'
    cards=[('Warehouse-SKU records',fmt(totals['skus'])),('Inventory value',money(totals['value'])),
           ('Below reorder point',fmt(totals['below_rop'])),('Negative available stock',fmt(totals['shortages']))]
    cards_html=''.join(f'<article class="metric"><span>{escape(k)}</span><strong>{escape(v)}</strong></article>' for k,v in cards)
    rows_html=''.join('<tr>'+''.join(f'<td>{escape(str(v))}</td>' for v in (
        r['whse'],r['part_no'],r['product_group'],r['available_qty'],r['reorder_point'],r['projected_available_qty']))+'</tr>' for r in risks)
    html="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ERP Inventory Intelligence | Data Engineering Demo</title>
<style>:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#142844;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{max-width:1300px;margin:auto;padding:40px 24px 65px}header{background:linear-gradient(120deg,#102642,#183e65);color:white;padding:48px 0}header .wrap{padding-top:0;padding-bottom:0}.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#87ddcf;font-weight:700}h1{font-size:clamp(28px,4vw,44px);line-height:1.13;margin:12px 0}header p{max-width:730px;color:#d7e3f0}a{color:#1265bb}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:0 0 24px}.metric,.panel{background:white;border:1px solid #e1e8f1;border-radius:14px;box-shadow:0 6px 22px #1731510b}.metric{padding:22px}.metric span{display:block;color:#667891;font-size:13px}.metric strong{display:block;font-size:clamp(22px,2.4vw,32px);margin-top:8px}.panel{padding:24px;margin-top:24px}h2{font-size:21px;margin:0 0 8px}.muted{color:#667891;font-size:13px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:12px 10px;text-align:left;border-bottom:1px solid #e6edf4}th{color:#60758d;font-size:12px;text-transform:uppercase}tr:hover{background:#f6f9fc}.scroll{overflow:auto}.footer{color:#60758d;font-size:13px;margin-top:26px}@media(max-width:760px){.metrics{grid-template-columns:repeat(2,1fr)}.panel{padding:12px}.wrap{padding:24px 14px}} </style></head><body>
<header><div class="wrap"><div class="eyebrow">SQL · DuckDB · Python · ETL</div><h1>ERP Inventory Intelligence</h1><p>From six synthetic ERP source tables to a validated warehouse–SKU inventory mart. Interactive analytics generated from SQL transformations, not a live ERP connection.</p></div></header>
<main class="wrap"><section class="metrics">__CARDS__</section><section class="panel"><h2>Inventory overview</h2><p class="muted">Hover to inspect values, zoom or toggle chart interactions. All figures are synthetic.</p>__GRAPH__</section><section class="panel"><h2>Replenishment watchlist</h2><p class="muted">12 largest gaps between available quantity and reorder point. Flags are indicators, not purchase recommendations.</p><div class="scroll"><table><thead><tr><th>Warehouse</th><th>SKU</th><th>Product group</th><th>Available</th><th>Reorder point</th><th>Projected available</th></tr></thead><tbody>__ROWS__</tbody></table></div></section><p class="footer">Synthetic demonstration dataset · Generated by the reproducible DuckDB SQL + Python ETL pipeline · No company data</p></main><script>__PLOTLY_JS__</script></body></html>"""
    html=html.replace('__CARDS__',cards_html).replace('__GRAPH__',graph).replace('__ROWS__',rows_html).replace('__PLOTLY_JS__',get_plotlyjs())
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(html,encoding='utf-8')
    print(f'Dashboard generated: {DEST} ({n} warehouse-SKU records)')
    return DEST

if __name__=='__main__':
    build_dashboard()
