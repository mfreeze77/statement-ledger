"""Bounded synthetic SQLite/FTS benchmark. Not a real-corpus or provider benchmark."""
from pathlib import Path
import argparse,json,platform,statistics,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from statement_ledger.store import Store
from statement_ledger.service import Ledger
from statement_ledger.claim_library import search_claims

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--records',type=int,default=10000)
    p.add_argument('--out',type=Path,default=ROOT/'validation/claim-index-benchmark.json')
    a=p.parse_args()
    if not 1<=a.records<=100000:p.error('--records must be 1..100000')
    with tempfile.TemporaryDirectory(prefix='statement-ledger-benchmark-') as tmp:
        path=Path(tmp)/'synthetic.sqlite3';store=Store(path);ledger=Ledger(store)
        try:
            started=time.perf_counter()
            for i in range(a.records):
                ledger.put('proposition',{'id':f'benchmark-{i:08d}','kind':'ambiguous',
                    'text':f'Synthetic laboratory {i%71} reported {i%991} samples in synthetic region {i%101} during synthetic period {i%20}. Benchmark record {i}.',
                    'scope':{'entity':f'synthetic-lab-{i%71}','period':f'synthetic-period-{i%20}','metric':'synthetic sample count'}})
            seconds=time.perf_counter()-started
            latencies=[];returned=[]
            for q in range(50):
                t=time.perf_counter();result=search_claims(ledger,f'synthetic laboratory {q%71} samples',limit=20)
                latencies.append((time.perf_counter()-t)*1000);returned.append(len(result['items']))
            store.db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            result={'synthetic':True,'records':a.records,'python':platform.python_version(),'platform':platform.platform(),
                'ingest_seconds':seconds,'records_per_second':a.records/seconds,'searches':50,
                'median_search_ms':statistics.median(latencies),'p95_search_ms':sorted(latencies)[47],
                'all_queries_returned_20':all(n==20 for n in returned),'database_bytes':path.stat().st_size,
                'sqlite_version':store.db.execute('select sqlite_version()').fetchone()[0],
                'limitations':['Synthetic ambiguous records only; no real source ingestion, evidence graph, review cards, provider calls or speech processing.',
                'Single process/local filesystem; timings are not a scale guarantee and retrieval quality is not measured.']}
        finally:store.close()
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
