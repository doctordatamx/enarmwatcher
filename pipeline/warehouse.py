"""Rebuildable DuckDB/Parquet warehouse; public frontend uses partitioned JSON."""
import json
import duckdb,pyarrow as pa,pyarrow.parquet as pq
from .ingest import ROOT

def main():
    data=json.loads((ROOT/'public/data/platform.json').read_text(encoding='utf8'))
    output=ROOT/'data/warehouse';output.mkdir(exist_ok=True)
    tables={'fact_academic':data['academic_records'],'fact_receiving_matrix':data['receiving'],'fact_receiving_sites':data['sites'],'dim_sources':data['sources']}
    with duckdb.connect(str(output/'enarm.duckdb')) as con:
        for name,rows in tables.items():
            arrow=pa.Table.from_pylist(rows);pq.write_table(arrow,output/(name+'.parquet'),compression='zstd');con.register('incoming',arrow);con.execute(f'CREATE OR REPLACE TABLE {name} AS SELECT * FROM incoming');con.unregister('incoming')
        con.execute('CREATE OR REPLACE VIEW national_academic AS SELECT year, SUM(examined) AS examined, CASE WHEN COUNT(selected)=COUNT(*) THEN SUM(selected) END AS selected FROM fact_academic GROUP BY year')
        con.execute('CREATE OR REPLACE VIEW institutional_offer AS SELECT year,institution_id,SUM(places) AS places FROM fact_receiving_matrix GROUP BY year,institution_id')
    print('DuckDB and four Zstandard Parquet tables built')

if __name__=='__main__':main()
